import discord
import re
import requests

client = discord.Client()



@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.content.startswith('/stock'):
        return
    

    command = message.content.split(' ')[1]
    stock = message.content.split(' ')[2]

    if command == 'price':
        quote = getQuote(stock)
        embed = discord.Embed(
            title = quote['01. symbol'],
            color = discord.Color.dark_red() if quote['09. change'].startswith('-') else discord.Color.dark_green()
        )
        embed.add_field(
            name = '{:.2f} USD'.format(float(quote['05. price'])),
            value = '{:.2f} USD ({})'.format(float(quote['09. change']), quote['10. change percent']),
            inline = False
        )
        await message.channel.send(embed=embed)

    elif command == 'quote':
        quote = getQuote(stock)
        embed = discord.Embed(
            title = quote['01. symbol'],
            color = discord.Color.dark_red() if quote['09. change'].startswith('-') else discord.Color.dark_green()
        )
        embed.add_field(
            name = '{:.2f} USD'.format(float(quote['05. price'])),
            value = '{:.2f} USD ({})'.format(float(quote['09. change']), quote['10. change percent']),
            inline = False
        )

        embed.add_field(
            name = 'Low',
            value = '{:.2f} USD'.format(float(quote['04. low'])),
            inline = True
        )
        embed.add_field(
            name = 'High',
            value = '{:.2f} USD'.format(float(quote['03. high'])),
            inline = True
        )

        embed.add_field(
            name = 'Volume',
            value = '{}'.format(quote['06. volume']),
            inline = False
        )

        embed.add_field(
            name = 'Previous Close',
            value = '{:.2f} USD'.format(float(quote['08. previous close'])),
            inline = True
        )
        embed.add_field(
            name = 'Open',
            value = '{:.2f} USD'.format(float(quote['02. open'])),
            inline = True
        )

        embed.add_field(
            name = 'Latest trading day',
            value = '{}'.format(quote['07. latest trading day']),
            inline = False
        )

        await message.channel.send(embed=embed)

    elif command == 'track':

        interval = re.search(r'interval=([0-9]*)', message.content)
        if not interval == None:
            interval = interval.group(1)
        
        change = re.search(r'change=(\$?[0-9]*\%?)', message.content)
        if not change == None:
            change = change.group(1)

        response = 'Provide at least one argument for interval or change.'

        if not interval == None:
            if interval == '':
                response = 'Interval time should be a number.'
            elif int(interval) <= 5:
                response = 'Interval time is too small (must be at least 5).'
            else:
                response = 'Tracking stock {} every {} seconds.'.format(stock, interval)

        if not change == None:
            if change.startswith('$'):
                unit = 'dollars'
            elif change.endswith('%'):
                unit = 'percent'
            amount = int(re.search(r'([0-9]+)', change))
            response += '\nTracking stock {} for changes greater than {} {}.'.format(stock, amount, unit)

        await message.channel.send(response)
        



    else:
        await message.channel.send("""
        Recognized commands:
        price <stock>: report the current price and change in price for a stock
        quote <stock>: display the current global quote for a stock
        track <stock> interval=<interval> change=<change>: report the quote for a stock every interval or when it changes by a certain amount
        """)
        

with open('apikey.txt', 'r') as apikeytxt:
    api_key = apikeytxt.read()
api_url = 'https://www.alphavantage.co/query'
def getQuote(symbol):
    data = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': api_key
    }
    return requests.get(api_url, params=data).json()['Global Quote']



with open('token.txt', 'r') as tokentxt:
    client.run(tokentxt.read())