import string
import json
from django.shortcuts import render,HttpResponse
from bs4 import BeautifulSoup
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
import requests

class country_info(APIView):

# Create your views here.
    def get(self,request,pk):
        u_i = string.capwords(pk)
        lists = u_i.split()
        word = "_".join(lists)
        print(word)

        html_text = requests.get('https://en.wikipedia.org/wiki/'+word).text
        soup = BeautifulSoup(html_text, 'lxml')
        main_table = soup.find('table', class_='infobox ib-country vcard')

        # flag url
        # print("----------------------------------------")
        flag_td = main_table.find('td', class_='infobox-image')
        # print(flag_td)
        # print("----------------------------------------")
        flag_url = flag_td.find('a', class_='image')
        flag_src = flag_url.find('img')
        final_url = flag_src.get('src')
        print(final_url)

        # for capital
        table = soup.find('table', {'class': 'infobox ib-country vcard'})
        val = table.find_all('tr')

        def get_value(value):
            all_a = value.find_all('a')
            output = []
            for i in all_a:
                output.append(i.text)

            return output

        def all_tr_val(table):
            all_tr = []
            for tr in val:
                th = tr.find_all('th', {'class': 'infobox-label'})
                if (len(th) > 0):
                    all_tr.append(tr)

            return all_tr

        def get_capital_and_city(all_tr):
            required_info = {}
            output = {}
            required_val = ["Capital", "Largest city"]
            for tr_val in all_tr:
                th = tr_val.find('th', {'class': 'infobox-label'})
                # print(str(th.text).lower().replace(" ",""))

                if th.text in required_val:
                    # print("found ",th.text)
                    required_info[th.text] = tr_val

            for key in required_info:
                data = get_value(required_info[key])
                output[key] = data

            return output

        all_tr = all_tr_val(val)
        ans1 = get_capital_and_city(all_tr)
        if word=="China":
            final_capital = ans1['largestcitybypopulation']
        else:
            final_capital = ans1['Capital']
#-----------------------------------------------------------------------------------------
        # for largest cities
        cities = ans1['Largest city']
        # area total
        def get_area_population_gdp(table):
            merged_row_tr = table.find_all('tr', {'class': 'mergedrow'})
            td_val = []
            output = {}

            for i in merged_row_tr:
                infoTd = i.find_all('td', {"class": 'infobox-data'})
                for val in infoTd:
                    td_val.append(val.text)

            for i, val in enumerate(td_val):
                if 'km2' in val:
                    output["area_total"] = val
                    output['population'] = td_val[i + 1]
                    output['GDP_nominal'] = td_val[i + 4]
                    break

            return output

        ans2 = get_area_population_gdp(table)
        total_area = ans2["area_total"]
        Population = ans2["population"]
        gdp = ans2["GDP_nominal"]

        # adding http to the final url

        #-------------------------------------------------------------------------------
        #for official languages
        # for official languages
        lang_tr = main_table.find('tr', class_='mergedtoprow')
        # print(lang_tr)
        lang_a = lang_tr.find_all('a')
        # print(lang_a)
        languages = []
        main_languages = []
        for j in lang_a:
            languages.append(j.text)
        # print(languages)

        for i in languages:
            if len(i) > 4:
                main_languages.append(i)
        print(main_languages)

        import re
        def formaturl(url):
            if not re.match('(?:http|ftp|https)://', url):
                return 'http:{}'.format(url)
            return url
        final_url = formaturl(final_url)
        print(final_url)

        ans = {
            'flag_link':final_url,
            'capital':final_capital,
            'largest_city':cities,
            'official_languages':main_languages,
            'area_total':total_area,
            'Population':Population,
            'GDP_Nominal':gdp,
        }
        #res = json.dumps(ans,indent=8)
        #print(res)
        return Response(ans,status=200)