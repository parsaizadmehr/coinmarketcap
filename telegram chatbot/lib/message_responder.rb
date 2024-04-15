require './models/user'
require './models/crypto'
require './lib/message_sender'

class MessageResponder
  attr_reader :message
  attr_reader :bot
  attr_reader :user

  def initialize(options)
    @bot = options[:bot]
    @message = options[:message]
    @user = User.find_or_create_by(uid: message.from.id)
  end

  def respond
    on /^\/start/ do
      answer_with_greeting_message
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

    on /^\/stop/ do
      answer_with_farewell_message
    end
  end

  private

  def on regex, &block
    regex =~ message.text

    if $~
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
    coin_info = coins.map {|coin| "#{coin.rank}) #{coin.name}"}.join("\n")
    msg = "Here is top coins: \n #{coin_info}"

    MessageSender.new(bot: bot, chat: message.chat, text: msg).send
  end
    
  def coin_rank_history(coin_symbol)
    coin_symbol.upcase!
    
    last_week_date = Date.today - 7
    last_week_record = HistoricalData.where(symbol: coin_symbol).where("date <= ?", last_week_date).order(date: :desc).first
    
    last_month_date = Date.today.prev_month
    last_month_record = HistoricalData.where(symbol: coin_symbol).where("date <= ?", last_month_date).order(date: :desc).first
  
    last_year_date = Date.today.prev_year
    last_year_record = HistoricalData.where(symbol: coin_symbol).where("date <= ?", last_year_date).order(date: :desc).first
  
    last_three_years_date = Date.today.prev_year(3)
    last_three_years_record = HistoricalData.where(symbol: coin_symbol).where("date <= ?", last_three_years_date).order(date: :desc).first
  
    msg = "Rank history for #{coin_symbol}:\n"
    msg += last_week_record ? "Last week: #{last_week_record.rank}\n" : "No record found for last week.\n"
    msg += last_month_record ? "Last month: #{last_month_record.rank}\n" : "No record found for last month.\n"
    msg += last_year_record ? "Last year: #{last_year_record.rank}\n" : "No record found for last year.\n"
    msg += last_three_years_record ? "Last three years: #{last_three_years_record.rank}\n" : "No record found for last three years.\n"
  
    MessageSender.new(bot: bot, chat: message.chat, text: msg).send
  
  end

  def compare_ranks
    coins = Cryptocurrency.select(:name, :rank, :last_update).order(:rank, last_update: :desc)
    
    last_ranks = {}
  
    rank_changes = {}
  
    coins.each do |coin|
      next unless coin.rank && coin.last_update
  
      next if last_ranks[coin.name] == coin.rank
  
      last_rank = Cryptocurrency.where(name: coin.name).where.not(rank: nil).order(last_update: :desc).limit(2).pluck(:rank).reverse
  
      if last_rank.length == 2
        rank_change = last_rank.first - last_rank.last
        if rank_change != 0 # Include only if there's a rank change
          change_symbol = rank_change.positive? ? "-" : "+"
          rank_changes[coin.name] = { change: rank_change, text: "#{coin.name} to #{last_rank.first} (#{change_symbol}#{rank_change.abs})" }
        end
      end
  
      last_ranks[coin.name] = coin.rank
    end
  
    sorted_rank_changes = rank_changes.values.sort_by { |change| change[:change].abs }.reverse
  
    msg = sorted_rank_changes.any? ? sorted_rank_changes.map { |change| change[:text] }.join("\n") : "No rank changes detected."
  
    MessageSender.new(bot: bot, chat: message.chat, text: msg).send
  end
  
end
