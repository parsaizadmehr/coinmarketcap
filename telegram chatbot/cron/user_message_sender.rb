require 'telegram/bot'
require 'yaml'
# require 'open-uri'

# def get_public_ip
#   URI.open('http://whatismyip.akamai.com').read
# end

# puts get_public_ip

config = YAML.load_file('../config/secrets.yml')
bot_token = config['telegram_bot_token']

def send_message_to_user(bot_token, chat_id, message_text)
  Telegram::Bot::Client.run(bot_token) do |bot|
    bot.api.send_message(chat_id: chat_id, text: message_text)
  end
end

user_uid = 363174278
user_name = "Parsa"

send_message_to_user(bot_token, user_uid, "Hello, #{user_name}! This is a test message.")
