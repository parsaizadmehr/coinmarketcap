require 'pg'
require '../models/crypto'
require 'date'

db_config = YAML.load(File.read('../config/database.yml'))
ActiveRecord::Base.establish_connection(db_config)


def coin_rank_history(coin_symbol)
  last_week_date = Date.today - 7
  last_week_record = TestTable.where(symbol: coin_symbol).where("date <= ?", last_week_date).order(date: :desc).first
  if last_week_record
    puts "Rank for #{coin_symbol} on last week: #{last_week_record.rank}"
  else
    puts "No record found for #{coin_symbol} within the last week."
  end
  
  last_month_date = Date.today.prev_month
  last_month_record = TestTable.where(symbol: coin_symbol).where("date <= ?", last_month_date).order(date: :desc).first
  if last_month_record
    puts "Rank for #{coin_symbol} on last month: #{last_month_record.rank}"
  else
    puts "No record found for #{coin_symbol} within the last month."
  end

  last_year_date = Date.today.prev_year
  last_year_record = TestTable.where(symbol: coin_symbol).where("date <= ?", last_year_date).order(date: :desc).first
  if last_year_record
    puts "Rank for #{coin_symbol} on last year: #{last_month_record.rank}"
  else
    puts "No record found for #{coin_symbol} within the last year."
  end

  last_three_years_date = Date.today.prev_year(3)
  last_three_years_record = TestTable.where(symbol: coin_symbol).where("date <= ?", last_three_years_date).order(date: :desc).first
  if last_three_years_record
    puts "Rank for #{coin_symbol} within the last three years: #{last_three_years_record.rank}"
  else
    puts "No record found for #{coin_symbol} within the last three years."
  end

end

# Call the method with the desired cryptocurrency symbol
coin_rank_history("BTC")
