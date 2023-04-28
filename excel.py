import xlsxwriter
import xlsxwriter.utility
import datetime
import db

def generate_summary():
    categories = db.get_all_categories()

    transactions = db.get_all_transactions()

    # Start from the first cell. Rows and columns are zero indexed.
    row = 0
    col = 0

    # Iterate over the data and write it out row by row.
    data = {}
    lastYear = -1
    lastMonth = -1
    lastCategory = ""
    for year, month, value, category, note, date in transactions:
        if year != lastYear:
            data[year] = {}
            lastYear = year
        if month != lastMonth:
            data[lastYear][month] = {"transactions": [], "categories": {}}
            lastMonth = month
        if category != lastCategory:
            data[lastYear][lastMonth]["categories"][category] = {"transactions": []}
            lastCategory = category

        data[lastYear][lastMonth]["categories"][category]["transactions"].append({
            "value": value,
            "note": note,
            "date": date
        })

        data[lastYear][lastMonth]["transactions"].append({
            "value": value,
            "category": category,
            "note": note,
            "date": date
        })

        for y in data:
            generate_year_summary(data[y], y)


def generate_year_summary(year_data, year):
    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook('summary' + year + '.xlsx')

    for month_data in year_data:
        worksheet = workbook.add_worksheet()
        worksheet.name = month_data
        generate_month_summary(year_data[month_data], worksheet)

    workbook.close()


def generate_month_summary(month_data, worksheet):
    worksheet.write(0, 0, "Totale")
    row = 1
    for data in month_data["transactions"]:
        worksheet.write(row, 0, data["date"])
        worksheet.write(row, 1, data["category"])
        worksheet.write(row, 2, data["value"])
        worksheet.write(row, 3, data["note"])
        row += 1

    col = 4
    for data in month_data["categories"]:
        col = generate_category_summary(month_data["categories"][data], data, col+1, worksheet)

    worksheet.write(row, 0, 'Total')
    worksheet.write(row, 1, '=SUM(C:C)')
    worksheet.autofit()


def generate_category_summary(category_data, name, column, worksheet):
    worksheet.write(0, column, name)
    row = 1
    for data in category_data["transactions"]:
        worksheet.write(row, column+0, data["date"])
        worksheet.write(row, column+1, data["value"])
        worksheet.write(row, column+2, data["note"])
        row += 1

    col_name = xlsxwriter.utility.xl_col_to_name(column+1)
    worksheet.write(row, column+0, 'Total')
    worksheet.write(row, column+1, '=SUM(' + col_name + '1:' + col_name + str(row) + ')')

    return column+3


#db.init()
#generate_summary()