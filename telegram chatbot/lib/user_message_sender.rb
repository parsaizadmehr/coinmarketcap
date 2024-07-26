# lib/user_message_sender.rb
require './lib/message_sender'
require './lib/app_configurator'
require './models/crypto'
require './models/user'

class UserMessageSender
  attr_reader :bot
  attr_reader :logger

  def initialize(bot)
    @bot = bot
    @logger = AppConfigurator.new.get_logger
  end

  def send_top_coins_to_all_users
    users = User.all
    coins = Cryptocurrency.limit(50).order(:rank)
    coin_info = coins.map { |coin| "#{coin.rank}) #{coin.name}" }.join("\n")
    msg = "Here are the top coins: \n#{coin_info}"

    users.each do |user|
      send_message(user.uid, msg)
    end
  end

  def send_compare_ranks_to_all_users
    sql = <<-SQL
      WITH ranked_cryptocurrencies AS (
          SELECT
              id,
              rank,
              symbol,
              name,
              price,
              percent_change_1h,
              percent_change_24h,
              percent_change_7d,
              market_cap,
              volume_24h,
              circulating_supply,
              last_update,
              ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY last_update DESC) AS rn
          FROM
              cryptocurrencies
      )
      SELECT
          current.symbol,
          current.name,
          current.rank AS current_rank,
          previous.rank AS previous_rank,
          (previous.rank - current.rank) AS rank_change,
          current.price AS current_price,
          previous.price AS previous_price,
          current.percent_change_1h AS current_percent_change_1h,
          previous.percent_change_1h AS previous_percent_change_1h,
          current.percent_change_24h AS current_percent_change_24h,
          previous.percent_change_24h AS previous_percent_change_24h,
          current.percent_change_7d AS current_percent_change_7d,
          previous.percent_change_7d AS previous_percent_change_7d,
          current.market_cap AS current_market_cap,
          previous.market_cap AS previous_market_cap,
          current.volume_24h AS current_volume_24h,
          previous.volume_24h AS previous_volume_24h,
          current.circulating_supply AS current_circulating_supply,
          previous.circulating_supply AS previous_circulating_supply,
          current.last_update AS current_last_update,
          previous.last_update AS previous_last_update
      FROM
          ranked_cryptocurrencies current
      LEFT JOIN
          ranked_cryptocurrencies previous
      ON
          current.symbol = previous.symbol
          AND previous.rn = 2
      WHERE
          current.rn = 1;
    SQL

    results = ActiveRecord::Base.connection.execute(sql)

    msg = "📊The most changed ranks:\n"

    if results.any?
      results.each do |result|
        rank_change = result['rank_change']
        if rank_change != 0
          msg += "#{result['symbol']} #{result['current_rank']}, (#{rank_change.positive? ? '+' : '-'}#{rank_change.abs})\n"
          logger.debug("#{result['symbol']} #{result['current_rank']}, Rank Change: #{rank_change}")
        end
      end

      last_update = results[0]['current_last_update'].strftime('%d-%m-%Y %H:%M')
      msg += "\nLast update: #{last_update}"
      logger.debug("Last update: #{last_update}")
    else
      msg = 'No rank changes detected.'
      logger.debug(msg)
    end

    users = User.all
    users.each do |user|
      send_message(user.uid, msg)
    end
  end

  private

  def send_message(uid, text)
    chat = { id: uid }
    MessageSender.new(bot: bot, chat: chat, text: text).send
  end
end
