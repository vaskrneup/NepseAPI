import requests
from bs4 import BeautifulSoup
import crayons
import logging
import datetime

# ---------------------------  DATA FORMAT !   ----------------------------------------------
# data = {"11-11-2011": {"10:11:11":
#                            {"tnt": 1111, "tat": 11111, "tst": 12131,
#                             "data": [[1, 123123, 12312, 3, 12, 31, 23, 123],
#                                      [123123, 12, 31, 23, 12, 3, 3, 4, ]]
#                             }
#                        },
#         "12-11-2011": {"10:11:11":
#                            {"tnt": 1111, "tat": 11111, "tst": 12131,
#                             "data": [[1, 123123, 12312, 3, 12, 31, 23, 123],
#                                      [123123, 12, 31, 23, 12, 3, 3, 4, ]]
#                             }
#                        }
#         }
# # -----------------------------------------------------------------------------------------------

# configure logger !
logging.basicConfig(filename='data.log', level=logging.DEBUG, filemode="a")


# for logging messages #easier !
def logger(msg, log_type="msg", output=True):
    if log_type == "msg":
        if output:
            print(crayons.green(f"[+] {msg}"))
        logging.info(msg)
    elif log_type == "war":
        if output:
            print(crayons.yellow(f"[!] {msg}"))
        logging.warning(msg)
    elif log_type == "err":
        if output:
            print(crayons.red(f"[-] {msg}"))


# grabs html from requested url !
def get_html(url: str) -> str or None:
    try:
        logger(f"Requesting data from {url} !")
        req = requests.get(url)
        # check for valid status !
        if req.status_code == 200:
            logger(f"Valid url {url} !")

            logger(f"Grabbed data for {url} !")
            return req.text
        else:
            return None
    # catch any exceptions !
    except Exception as e:
        logger(f"Fatal error in get_html() --> '{e}'", log_type="err")
        return None


# takes url and returns soup using get_html() !
def get_soup(url: str) -> BeautifulSoup:
    try:
        html_text = get_html(url)
        if html_text:
            soup = BeautifulSoup(html_text, "lxml")
        else:
            soup = BeautifulSoup("", "lxml")
        return soup

    except Exception as e:
        logger(f"Fatal error in get_soup() --> '{e}'")
        return BeautifulSoup("", "lxml")


# creates data in required format !
def parse_nepse_data(soup: BeautifulSoup):
    try:
        # select td TAG that is inside tr TAG !
        data_table = soup.select("tr > td")

        # for encoding every company data in different list !
        c = 0
        # for single company data !
        x = []
        # for handling x !
        y = []

        # last list is not appended to y, for further use in PART-2 !
        for i in range(11, len(data_table)):
            # remove spaces from data !
            col = data_table[i].text.strip()

            # check for null lines !
            if len(col) != 0:
                # check for individual company data !
                if c != 10:
                    x.append(col)
                    c += 1
                # for appending all details about single company !
                else:
                    y.append(x)
                    x = [col]
                    c = 1

        # PART-2 !
        final_data = {
            "total_amount_rs": float(x[2].replace(",", "")),
            "total_quantity": int(x[4].replace(",", "")),
            "total_num_of_transactions": int(x[6].replace(",", "")),
            "company_data": y
        }

        return final_data if len(y) > 10 else None
    except Exception as e:
        logger(f"Fatal error in parse_nepse_data() --> {e}", log_type="err")
        return None


# grabs data for html for series of dates !
def get_nepse_data(start_date, end_date) -> dict:
    """
    :param end_date: dd-mm-yyyy
    :param start_date: dd-mm-yyyy
    """
    start_date = start_date.split("-")
    end_date = end_date.split("-")

    start_date = datetime.date(day=int(start_date[0]), month=int(start_date[1]), year=int(start_date[2]))
    end_date = datetime.date(day=int(end_date[0]), month=int(end_date[1]), year=int(end_date[2]))

    if start_date > end_date:
        logger("start date is greater than end date !", log_type="err")
        raise ValueError("Start date is greater then end date !")

    else:
        # for increasing date by 1 day in every loop !
        delta = datetime.timedelta(days=1)

        final_data = {}

        # using all other functions create data in json format !
        while start_date <= end_date:
            # create source url !
            link = f"http://nepalstock.com.np/todaysprice?startDate=" \
                   f"{start_date.year}-{start_date.month}-{start_date.day}" \
                   f"&stock-symbol=&_limit=500"
            # grab soup for that url !
            soup = get_soup(link)
            # get company data from soup !
            data = parse_nepse_data(soup=soup)

            # check if market was open on that date !
            if data:
                final_data[str(start_date)] = {"16:00:00": data}
            else:
                logger(f"Market seems to be closed in {str(start_date)} !", log_type="war")

            # increment date by 1 day !
            start_date += delta

        return final_data


_ = get_nepse_data("19-02-2020", "23-02-2020")
print(_)
