import re
import pandas as pd
from botasaurus.browser import browser, Driver
from bs4 import BeautifulSoup


def clean_name(pilot:str):
    counter = -1
    name = ""
    puntation = 0
    position = ""
    for p in pilot:
        if p.isnumeric():
            position += p
        if  p.isupper() or  p.isnumeric() :
            counter +=1
            continue
        else:
            name = pilot[counter:]
            frist_digit = re.search(r"\d",name ).start()
            puntation =name[frist_digit:]
            name = name[:frist_digit]
            break
    return position,name,puntation

def get_competicion(html_info):
    soup = BeautifulSoup(html_info)
    competicion = soup.find_all("thead",{"class":"Table__header-group Table__THEAD" }) 
    competicion = competicion[1]
    all_competicion = competicion.find_all("span",{"class":"fw-medium w-100 dib tar subHeader__item--content underline" })
    list_cirucit=[]
    for comp in all_competicion:
       circuit = comp.attrs["title"]
       list_cirucit.append(circuit)
    return list_cirucit
    
def get_points(html_info:str,list_circuit:list ):
    soup = BeautifulSoup(html_info)
    table_point = soup.find_all("tbody",{"class":"Table__TBODY" } )
    table_point = table_point[1]
    row = table_point.find_all("tr")
    final_table = {}
    general_list = []
    for cell in row:
        list_point_in_row =[]
        counter = 0
        row={}        
    
        all_poins = cell.find_all("td")
        for point in all_poins:
            circuit_name = list_circuit[counter]
            row[circuit_name] =[point.text]
            counter +=1
        general_list.append(row)
        
    return general_list        

def get_position(html_page:str,year:str="2024"):
    soup = BeautifulSoup(html_page)
    pilot_table = soup.find("tbody",{"class" :"Table__TBODY"} )
    list_position = []
    information_piolots = pilot_table.find_all("tr")
    for pilot in information_piolots:
        name = pilot.text
        nationality = pilot.find("img")
        try:
            nationality = nationality.attrs.get("alt" )
        except: 
            nationality = ""
        position, name,putation = clean_name(name)
        info_pilot={
            "name":[name],
            "position":[position],
            "puntation":[putation],
            "nationality":[nationality],
            "year":[year]
        }
        df = pd.DataFrame(info_pilot)
        list_position.append(df) 
    df = pd.concat(list_position)         
    return df

def get_position_comany(html_page:str,year:str="2024"):
    soup = BeautifulSoup(html_page)
    pilot_table = soup.find("tbody",{"class" :"Table__TBODY"} )
    list_position = []
    information_piolots = pilot_table.find_all("tr")
    for pilot in information_piolots:
        name = pilot.text
        position, name,putation = clean_name(name)
        info_pilot={
            "name":[name],
            "position":[position],
            "puntation":[putation],
            "year":[year]
        }
        df = pd.DataFrame(info_pilot)
        list_position.append(df) 
    df = pd.concat(list_position)         
    return df

def get_years_competision(html_page:str):
    soup = BeautifulSoup(html_page)
    years = soup.find_all("option",{"class":"dropdown__option" } )
    list_years   = []
    for year in years:
        year_url = year.attrs["data-url"]
        list_years.append( (year.text,year_url ))
    return list_years

def create_table_points(html_info):
    circuits = get_competicion(html_info=html_info)
    list_row_points = get_points(html_info=html_info,list_circuit=circuits)
    list_df = []
    for row in list_row_points:
        df = pd.DataFrame( row)
        list_df.append(df)
    final_df = pd.concat(list_df,)
    return final_df

@browser
def browser_extracter(driver: Driver,data):
    driver.get("https://www.espn.com.mx/deporte-motor/f1/posiciones")    
    html_value = driver.page_html
    all_years = get_years_competision(html_page=html_value)
    list_df =[]
    for year,url in all_years:
        url_espn = "https://www.espn.com.mx/"
        url_espn += url
        driver.get(link=url_espn)
        html_page = driver.page_html
        position = get_position(html_page=html_page,year=year)
        position.insert(0, 'ID', range(1, 1 + len(position)))
        tables = create_table_points(html_info=html_page )
        tables.insert(0, 'ID', range(1, 1 + len(tables)))
        final_table = position.merge(tables, on="ID")
        list_df.append(final_table)
        df  = pd.concat(list_df)
    del df["ID"]
    df.insert(0, 'ID', range(1, 1 + len(df)))
    df.to_csv("posiciones.csv")
    driver.get("https://www.espn.com.mx/deporte-motor/f1/posiciones/_/grupo/construtores")
    html_page = driver.page_html
    years = get_years_competision(html_page=html_page)
    list_df = []
    for year, url in years:
        espn_url = "https://www.espn.com.mx/" + url
        driver.get(espn_url)
        html_page = driver.page_html
        position = get_position_comany(html_page=html_page,year=year )
        position.insert(0, 'ID', range(1, 1 + len(position)))
        tables = create_table_points(html_info=html_page )
        tables.insert(0, 'ID', range(1, 1 + len(tables)))
        final_table = position.merge(tables, on="ID")
        list_df.append(final_table)
    df  = pd.concat(list_df)
    del df["ID"]
    df.insert(0, 'ID', range(1, 1 + len(df)))
    df.to_csv("companias.csv")
    
    print("Hola")
    driver.close()

browser_extracter()

