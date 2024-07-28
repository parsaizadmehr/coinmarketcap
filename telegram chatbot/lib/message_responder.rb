require 'English'
require_relative '../models/user'
require_relative '../models/crypto'
require_relative 'message_sender'
require_relative 'app_configurator'

class MessageResponder
  attr_reader :message
  attr_reader :bot
  attr_reader :user
  attr_reader :logger

  def initialize(options)
    @bot = options[:bot]
    @message = options[:message]
    @user = User.find_or_create_by(uid: message.from.id)
    @logger = AppConfigurator.new.get_logger
  end

  def respond
    on /^\/start/ do
      answer_with_greeting_message
    end

    on /^\/stop/ do
      answer_with_farewell_message
    end

    on /^\/top/ do
      top_coins
    end

    on /^\/c (.+)/ do |coin_symbol|
      coin_rank_history(coin_symbol)
    end

    on /^\/compare_ranks/ do
      compare_ranks
    end
  end


  private

  def on(regex, &block)
    regex =~ message.text

    if $LAST_MATCH_INFO
      case block.arity
      when 0
        yield
      when 1
        yield $1
      when 2
        yield $1, $2
      end
    end
  end

  def answer_with_greeting_message
    answer_with_message I18n.t('greeting_message')
  end

  def answer_with_farewell_message
    answer_with_message I18n.t('farewell_message')
  end

  def answer_with_message(text)
    MessageSender.new(bot: bot, chat: message.chat, text: text).send
  end

  def top_coins
    coins = Cryptocurrency.limit(50).order(:rank)
    coin_info = coins.map { |coin| "#{coin.rank}) #{coin.name}" }.join("\n")
    msg = "Here is top coins: \n#{coin_info}"

    answer_with_message(msg)
  end

  def coin_rank_history(coin_symbol)
    coin_symbol.upcase!

    last_week_date = Date.today - 7
    last_week_record = HistoricalData.where(symbol: coin_symbol)
                                     .where('date <= ?', last_week_date)
                                     .order(date: :desc).first
    last_month_date = Date.today.prev_month
    last_month_record = HistoricalData.where(symbol: coin_symbol)
                                      .where('date <= ?', last_month_date)
                                      .order(date: :desc).first
    last_year_date = Date.today.prev_year
    last_year_record = HistoricalData.where(symbol: coin_symbol)
                                     .where('date <= ?', last_year_date)
                                     .order(date: :desc).first
    last_three_years_date = Date.today.prev_year(3)
    last_three_years_record = HistoricalData.where(symbol: coin_symbol)
                                            .where('date <= ?', last_three_years_date)
                                            .order(date: :desc).first

    msg = "Rank history for #{coin_symbol}:\n"
    msg += last_week_record ? "Last week: #{last_week_record.rank}\n" : "No record found for last week.\n"
    msg += last_month_record ? "Last month: #{last_month_record.rank}\n" : "No record found for last month.\n"
    msg += last_year_record ? "Last year: #{last_year_record.rank}\n" : "No record found for last year.\n"
    msg += last_three_years_record ? "Last three years: #{last_three_years_record.rank}\n" : "No record found for last three years.\n"

    answer_with_message(msg)
  end

  def compare_ranks
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
      msg += "\n#{last_update}"
      logger.debug("Last update: #{last_update}")
    else
      msg = 'No rank changes detected.'
      logger.debug(msg)
    end
  
    answer_with_message(msg)
  end

end
