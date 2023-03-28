import sys

try:
    ini = sys.argv[1]
    ini = ini.split("&")
    a = ini[0].split("=")[1]
    b = ini[1].split("=")[1]

    c = ""
    c = ini[2].split("=")[1]

    res = ""

    with open("cgi-bin/cal_res.html", "r", encoding="utf-8") as f:
        for line in f:
            res += line
    res = res.replace("$a", a)
    res = res.replace("$b", b)

    if c == "mul":
        res = res.replace("$c","*")
        res = res.replace("$res", str(float(a) * float(b)))
    elif c == "div":
        res = res.replace("$c", "/")
        res = res.replace("$res", str(float(a) / float(b)))
    elif c == "add":
        res = res.replace("$c", "+")
        res = res.replace("$res", str(float(a) + float(b)))
    else:
        res = res.replace("$c", "-")
        res = res.replace("$res", str(float(a) - float(b)))

    res = res.replace("$hostname", sys.argv[2])
    res = res.replace("$port", sys.argv[3])
    print(res)

except:
    error_page = ""
    with open("400.html", "r", encoding="utf-8") as f:
        for line in f:
            error_page += line
    print(error_page)


