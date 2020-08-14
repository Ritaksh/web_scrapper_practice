

from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo

app =Flask(__name__)


@app.route('/', methods = ['POST','GET'])
def index():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ","")
        try:
            dbConn = pymongo.MongoClient('')
            db = dbConn['']
            reviews = db[searchString].find({})
            if reviews.count() > 0:
                return render_template('results.html', reviews = reviews)
            else:
                flipkart_url = 'https://www.flipkart.com/search?q=' + searchString
                uClient = uReq(flipkart_url)
                flipkartPage = uClient.read()
                uClient.close()
                flipkart_html = bs(flipkartPage,'html.parser')
                bigboxes = flipkart_html.findAll('"div", {"class": "bhgxx2 col-12-12"}')
                del bigboxes[0:3]
                box = bigboxes[0]
                productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
                prodRes = requests.get(productLink)
                prod_html = bs(prodRes.text, 'html.parser')
                commentboxes = prod_html.find_all('div', {'class':'_3nrCtb'})


                table = db[searchString]

                reviews = []

                for commentbox in commentboxes:
                    try:
                        name = commentbox.div.div.find_all('p', {'class': '_3LYOAd _3sxSiS'})[0].text

                    except:
                        name = 'No Name'

                    try:
                        rating = commentbox.div.div.div.div.text
                    except:
                        rating = 'No Rating'

                    try:
                        commentHead = commentbox.div.div.div.p.text

                    except:
                        commentHead = 'No Comment Heading'

                    try:
                        comtag = commentbox.div.div.find_all('div', {'class': ''})
                        custComment = comtag[0].div.text
                    except:
                        custComment = 'No Customer comment'

                    mydict = {'product': searchString, 'Name': name, 'Rating': rating,'commentHead':commentHead,'Comment': custComment}

                    x = table.insert_one(mydict)
                    reviews.append(mydict)

                return render_template('results.html', reviews = reviews)

        except:
            return 'Something is wrong'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(port=8000,debug=True)










