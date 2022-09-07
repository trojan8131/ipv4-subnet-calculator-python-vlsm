from errno import ESTALE
from ipaddress import IPv4Address, ip_address
from pydoc import describe
from traceback import print_tb
from ciscoconfparse import CiscoConfParse
import ipaddress
import xlsxwriter
from tabulate import tabulate



def split_ip(ip):
    return tuple(int(part) for part in ip.split('.'))

def my_key(item):
    return split_ip(item[0])

def split_ip2(ip):
    return tuple(int(part) for part in ip.split('.'))

def my_key2(item):
    return split_ip2(item[1])


def main(shift=0):

    ip_subnet=["10.10.0.0","32"]
    ip_subnet[1]=str(int(ip_subnet[1])+shift)

    networks=[]
    subnets=[]
    final=[]

    subnets.append(ip_subnet)

    file = open("network_gen.txt","r")
    for line in file:
        networks.append(line.strip('\n').split(";"))

    error=False

    while networks:
        for net in networks:
            if(error):
                shift-=1
                print("The netmask is too big, I'm reducing it to: "+str(int(ip_subnet[1])-1))
                main(shift)
                exit()
            else:
                error=True
            for sub in subnets:
                if int(net[1])==int(sub[1]):
                    final.append([net[0],sub[0],sub[1]])
                    networks.remove(net)
                    subnets.remove(sub)
                    error=False
                    break
                elif int(net[1])<int(sub[1]):
                    if subnets:
                        continue
                    else:
                        exit()
                elif int(net[1])>int(sub[1]):
                    network=ipaddress.IPv4Network(sub[0]+"/"+sub[1])  
                    network=list(network.subnets(prefixlen_diff=1))
                    subnets.remove(sub)
                    for i in network:
                        subnets.append([str(i.network_address),str(i.prefixlen)])
                    subnets=sorted(subnets, key=my_key)
                    error=False
                    break
                print(subnets)


    networks=sorted(final, key=my_key2)
    print("Leftover:")
    for i in subnets:
        print(i[0]+"/"+i[1])
    final1=[]
    print("############################")
    for i in networks:
        net=ipaddress.IPv4Network(i[1]+"/"+i[2])
        final1.append([i[0],i[1],i[2],str(len(list(net.hosts()))),str(list(net.hosts())[0]),str(list(net.hosts())[-1]),str(net.broadcast_address)])
    for i in networks:
        final
    print(tabulate(final1, headers=["Name","Network Address","Prefix","Number of hosts","Girst host","Last host","Broadcast"], tablefmt="grid"))





    ############################################################
    excel_path="subnets.xlsx"
    workbook = xlsxwriter.Workbook(excel_path)
    worksheet = workbook.add_worksheet("subnets")
    bold = workbook.add_format({'bold': True})
    row=0
    col=0
    #############################################################
    title=["Name","Network Address","Prefix","Number of hosts","Girst host","Last host","Broadcast"]
    for i in title:
        worksheet.write(row, col, i,bold)
        col+=1
    row+=1
    col=0

    for x in final1:
        for y in x:
            worksheet.write(row, col, y)
            col+=1
        col=0
        row+=1
    worksheet = workbook.add_worksheet("Leftover")
    title=["Network Address","Prefix"]
    row=0
    col=0
    for i in title:
        worksheet.write(row, col, i,bold)
        col+=1
    row+=1
    col=0
    for x in subnets:
        for y in x:
            worksheet.write(row, col, y)
            col+=1
        col=0
        row+=1    
    workbook.close()


main()
