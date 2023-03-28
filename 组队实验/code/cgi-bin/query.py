import sqlite3
import sys

try:
    ini = sys.argv[1]
    hostname = sys.argv[2]
    port = sys.argv[3]

    ini = ini.split("&")
    student_id = ini[0].split("=")[1]
    student_name = ini[1].split("=")[1]
    student_class = ini[2].split("=")[1]
    # value = " (" + student_id + ',"' + student_name + '","' + student_class + '")'

    # db = pymysql.connect(host="localhost",
    #                      user="root",
    #                      password="123456",
    #                      database="Student_data",
    #                      charset='utf8')
    # cursor = db.cursor()

    db = sqlite3.connect('data\Student_data.db')
    cursor = db.cursor()

    sql = "SELECT * from student"

    id_flag = 1
    id_name = 1
    id_class = 1

    if student_id == "":
        id_flag = 0
    if student_name == "":
        id_name = 0
    if student_class == "":
        id_class = 0

    if id_flag == 0 and id_name == 0 and id_class == 0:
        pass
    else:
        sql += " where"
        if id_flag == 1:
            sql += " id = " + student_id

        if id_flag == 0 and id_name == 1:
            sql += " name = \'" + student_name + "\' "
        elif id_flag == 1 and id_name == 1:
            sql += " and name = \'" + student_name + "\' "

        if id_flag == 0 and id_name == 0 and id_class == 1:
            sql += " class = \'" + student_class + "\' "
        elif id_class == 1:
            sql += " and class = \"" + student_class + "\" "

    sql += ";"

    try:
        cursor.execute(sql)
    except:
        print(sql)

    data = cursor.fetchall()
    res = ""

    # print()

    with open("cgi-bin/query_res.html", "r", encoding="utf-8") as f:
        #pass
        print(res)

    f.close()

    with open("cgi-bin/query_res.html", "r", encoding="utf-8") as f:
        # res_list = f.readlines()
        # for ress in res_list:
        #     res += ress
        for line in f:
            res += line

    student_data = ''
    for student in data:
        temp = "<tr>"
        temp += "<th>" + str(student[0]) + "</th>"
        temp += "<th>" + student[1] + "</th>"
        temp += "<th>" + student[2] + "</th>"
        temp += "</tr>\n"
        student_data += temp
    res = res.replace("$data", student_data)
    res = res.replace("$message", sql)
    res = res.replace("$test", res)

    print(res)

except:
    error_page = ""
    with open("400.html", "r", encoding="utf-8") as f:
        for line in f:
            error_page += line
    print(error_page)