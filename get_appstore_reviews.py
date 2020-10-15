import requests
import xml.etree.ElementTree as et
import csv
import sys


countries = {
    'fr', # France
    'ru', # Russia
    'us' # United States
}

def get_reviews(appId, country):

    page = 1

    reviews = []

    while True:
        
        entries = get_reviews_for_page(appId, country, page)

        if entries == None:
            break
        if len(entries) == 0:
            break

        page += 1

        for entry in entries:

            review = parse_review(entry)
            if review != None:

                review['country'] = country
                reviews.append(review)

    return reviews  


def get_reviews_for_page(appId, country, page):

    print("Start loading reviews for country: %s. Page: %d"  % (country, page))

    url = 'https://itunes.apple.com/%s/rss/customerreviews/page=%d/id=%s/sortBy=mostRecent/xml' % (country, page, appId)

    response = requests.get(url)

    root = et.fromstring(response.content)

    return root.findall('{http://www.w3.org/2005/Atom}entry')


def parse_review(entry):

    review = {}

    rss_prefix = '{http://itunes.apple.com/rss}'
    atom_prefix = '{http://www.w3.org/2005/Atom}'

    review["review_id"] = get_text_value_from_entry(entry, atom_prefix, 'id')    
    review["version"] = get_text_value_from_entry(entry, rss_prefix, 'version')
    review["rating"] = get_text_value_from_entry(entry, rss_prefix, 'rating')
    review["review"] = get_review_from_entry(entry)
    review["author"] = get_author_from_entry(entry)
    review["title"] = get_text_value_from_entry(entry, atom_prefix, 'title')
    review["updated"] = get_text_value_from_entry(entry, atom_prefix, 'updated')

    return review

def get_text_value_from_entry(entry, prefix, name):

    full_name = prefix + name

    value = entry.find(full_name)
    if value == None:
        return ''
    
    return value.text

def get_author_from_entry(entry):

    value = entry.find('{http://www.w3.org/2005/Atom}author')
    if value == None:
        return ''
    
    name = value.find('{http://www.w3.org/2005/Atom}name')
    if name == None:
        return ''
    
    return name.text

def get_review_from_entry(entry):

    for review in entry.findall('{http://www.w3.org/2005/Atom}content'):
        if review.get('type') == 'text':
            return review.text

    return ''





if len(sys.argv) < 2:
    print("Use: python get_appstore_reviews.py <app_id>")
    exit(1)

app_id = sys.argv[1]
if app_id == None:
    print("Use: python get_appstore_reviews.py <app_id>")
    exit(1)


all_reviews = []

for countryCode in countries:

    reviews = get_reviews(app_id, countryCode)

    all_reviews.extend(reviews)

csvTitles = [
    u'Id'.encode("utf-8"),
    u'Title'.encode("utf-8"),
    u'Author'.encode("utf-8"),
    u'App. Version'.encode("utf-8"),
    u'Rating'.encode("utf-8"),
    u'Review'.encode("utf-8"),
    u'Country'.encode("utf-8"),
    u'Date'.encode("utf-8")
    ]

with open('./result.csv', "w") as file:
    writer = csv.writer(file)
    writer.writerow(csvTitles)  

    for review in all_reviews:
        csvData = [
            review['review_id'].encode("utf-8"),  
            review['title'].encode("utf-8"),
            review['author'].encode("utf-8"),
            review['version'].encode("utf-8"),
            review['rating'].encode("utf-8"),
            review['review'].encode("utf-8"),
            review['country'].encode("utf-8"),
            review['updated'].encode("utf-8"),
            ]
        writer.writerow(csvData)