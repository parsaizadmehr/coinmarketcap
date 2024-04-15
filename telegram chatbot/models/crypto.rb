 
require 'active_record'


class Cryptocurrency < ActiveRecord::Base
  self.table_name = 'cryptocurrencies'
end

class HistoricalData < ActiveRecord::Base
  self.table_name = 'historical_data'
end

