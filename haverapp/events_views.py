from django.http import HttpResponse, Http404
from django.template import RequestContext
from django.shortcuts import render

from models import *

#Import the libraries to parse xml and strip it.
import urllib2
import datetime
from xml.etree import ElementTree
from django.utils.html import strip_tags


import re #Import regex expressions.

def events_bryn_mawr():
	raw_response = urllib2.urlopen("http://mc.brynmawr.edu/MasterCalendar/RSSFeeds.aspx?data=OiNeXA6LJItp%2bLkkMsbi49mAmSFb2aYs4cLs6ugMeyyRblb6fLj%2b2Q%3d%3d").read()
	xml_response = ElementTree.fromstring(raw_response)
        """
	product = ''
        for child  in xml_response:
                for grandchild in child.findall('item'):
                        product += '<div style="border:solid">'
                        product += '<h1>'+ grandchild[0].text.encode('utf-8')+'</h1>'
                        product += '<p>'+ grandchild[1].text.encode('utf-8')+'</p>'
                        product += '</div>'
        return HttpResponse(product)"""
	product=[{"title":grandchild[0].text,"description":grandchild[1].text,"url":grandchild[5].text, "pubDate":grandchild[4].text[:17]} for child in xml_response for grandchild in child.findall("item")]
	return product

def haverford_news():
	raw_response = urllib2.urlopen("http://www.haverford.edu/news/rss/").read()
	xml_response = ElementTree.fromstring(raw_response)
	product=[{"title":grandchild[0].text,"description":grandchild[1].text,"url":grandchild[5].text, "pubDate":grandchild[4].text[:17]} for child in xml_response for grandchild in child.findall("item")]
	return product



def events_haverford():
    raw_response = urllib2.urlopen("http://www.haverford.edu/goevents/").read()
    xml_response = ElementTree.fromstring(raw_response)
    """
        product = ''
        for child  in xml_response:
		product += u"<div style='border:solid'><div><h1>{0}</h1></div> <div>{1}</div>".format(child[0].text, child[1].text)
		product += str(child[2].text)
		product += '<br/>' +  str(child[3].text)+'</div>'
	product += '<a href="/events/"><div style="font-size:60pt;text-align:center">Back</div></a>'
    """
    product = [{"title":child[0].text,"date": child[1].text ,"time":child[2].text,"description":child[3].text} for child in xml_response]

    return product

def events_swarthmore():
        raw_response = urllib2.urlopen("http://calendar.swarthmore.edu/calendar/RSSSyndicator.aspx?category=&location=&type=N&binary=Y&keywords=&number=20&ics=Y").read()
        xml_response = ElementTree.fromstring(raw_response)

	"""
	product = ''
	for child in xml_response:
		for grandchild in child.findall("item"):
			product += '<div style="border:solid">'
			product += '<h1>'+ grandchild[0].text.encode('utf-8')+'</h1>'
			product += '<p>'+ grandchild[2].text.encode('utf-8')+'</p>'
			product += '</div>'
        return HttpResponse(product)
	"""
	product	= [{"title":grandchild[0].text, "url":grandchild[1].text, "description":grandchild[3].text[9:-3], "category":grandchild[5].text} for item in xml_response for grandchild in item.findall("item")]
	return product

# Written by Brandon on 12/5/2013
#
def events_upenn():
        raw_response = urllib2.urlopen("http://www.upenn.edu/calendar-export/?type=rss2&showndays=3").read()
        xml_response = ElementTree.fromstring(raw_response)
        """
	product = ''
        for child  in xml_response:
                for grandchild in child.findall('item'):
                        print grandchild[0].text
			product += '<div style="border:solid">'
                        product += '<h1>'+ grandchild[0].text.encode('utf-8')+'</h1>'
                        product += '<p>'+ grandchild[1].text.encode('utf-8')+'</p>'
                        product += '</div>'
        return HttpResponse(product)
	"""
	product = [{"title":grandchild[0].text, "description":strip_tags(grandchild[2].text), "url":grandchild[1].text, "pubDate":strip_tags(grandchild[2].text[:23])} for child in xml_response for grandchild in child.findall('item')]
        return product

#written by blair. last edited by blair 12/05/2013
def camp_philly_feed():
        raw_response = urllib2.urlopen("http://campusphilly.org/feed/").read()
        xml_response = ElementTree.fromstring(raw_response)

        product = []
        for child  in xml_response:
                for grandchild in child.findall('item'):
                        title = ""
			link = ""
			description = ""
			for great_grand in grandchild:
                                if great_grand.tag == "title":
                                        title =  great_grand.text.encode('utf-8')
                                if great_grand.tag == "link":
                                        link = great_grand.text.encode('utf-8')
                                if great_grand.tag == "description":
                                        description = great_grand.text.encode('utf-8')
                        final_product = {"title": title, "url": link, "description": description}
                        product.append(final_product)
                        #product += '<p>'+ grandchild[1].text.encode('utf-8')+'</p>'
        #return HttpResponse(product)

        return product


#The main EVENTS view that funnels view information into one easy-to-use template.
def events(request, page):
    #Variable Setup.
    template = "event_grid.html"
    back="events"

    if page=="haverford":
        data = events_haverford()
        title="Haverford"
    elif page=="brynmawr":
        data = events_bryn_mawr()
        title="Bryn Mawr"
    elif page=="swarthmore":
        data = events_swarthmore()
        title="Swarthmore"
    elif page=="upenn":
        data = events_upenn()
        title="UPenn"
    elif page=="campus_philly":
        data = camp_philly_feed()
        title= "Campus Philly"
    else:
        return HttpResponse("Events not found!")

    new_data = [[None, list()]]
    for entry in data:
	if "date" in entry.keys():
	    date = entry["date"]
	elif "category" in entry.keys():
	    date = entry["category"]
	elif "pubDate" in entry.keys():
	    date = entry["pubDate"]
	elif "description" in entry.keys():
	    date = entry["description"]
        if new_data[-1][0]==date:
            new_data[-1][1].append(entry)
        else:
	    if "date" in entry.keys():# works for haverford events
		new_data.append([entry["date"], [entry]])
	    elif "category" in entry.keys(): #this is for the swat events
		new_data.append([entry["category"], [entry]])
	    elif "pubDate" in entry.keys(): # this is for Bryn Mawr events
		new_data.append([entry["pubDate"], [entry]])
	    elif "description" in entry.keys(): #works for byrn mawr, but also a good default
		new_data.append([entry["description"], [entry]])

    new_data.pop(0)
    return render(request, "app_container.html", {"template":template, "data":new_data, "title": title, "back":back}    )


