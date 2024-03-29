 
# require necessary gems
require 'active_record'
# require 'yaml'

# db_config = YAML.load(File.read('../config/database.yml'))

# ActiveRecord::Base.establish_connection(db_config)

class Cryptocurrency < ActiveRecord::Base
  self.table_name = 'cryptocurrencies'
end

class HistoricalData < ActiveRecord::Base
  self.table_name = 'historical_data'
end

class TestTable < ActiveRecord::Base
  self.table_name = 'test_table'
end

# cryptocurrencies = Cryptocurrency.all

# cryptocurrencies.each do |crypto|
#   puts "Name: #{crypto.name} Price: #{crypto.price}"
# end

# ActiveRecord::Base.connection.close
