import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from ourfunctions import *
#getting current date in form of YYYY-MM-DD, which is the first part of datetime.datetime.now() string
#replacing '-' with '/' , splitting the datetime string by spaces into a list
#assigning the string value of the first index (of the created list) to current_date
current_date=((str(datetime.datetime.now()).replace('-','/')).split())[0]
#df=pd.read_csv('info.csv') #the main dataframe, containing information of the building's units
df=pd.read_excel('data1.xlsx')


##could be used to import new data (new bills info) by taking the input line directly from console
# vorudi=[]
# while True:
#     k=input()
#     if(k=='Exit'):
#         break
#     else:
#         vorudi.append(k.split())




##converting data2.xlsx rows to string lines, and saving it all in a text file: inputs.txt:
#creating dataframe of all bills and filtering out the ones not related to any unit ([]) 
data2=pd.read_excel('data2.xlsx')
data2=data2[data2['name']!='[]'].reset_index(drop=True)

#making slight changes in bills names
r_daste={'Ghabz':'ghabz','nezafat':'nezafat','asansor':'elevator','tamirat':'tamirat','parking':'parking','other':'other'}
data2['daste']=data2['daste'].map(r_daste)
r_zirdaste={'gaz':'gas','Water':'water','bargh':'electricity','avarez':'avarez','###':'undefined'}
data2['zirdaste']=data2['zirdaste'].map(r_zirdaste)

#changing date format from YYYY-MM-DD to YYYY/MM/DD, and creating a new column with dates of column "date", converted from jalali to gregorian dates
data2['date']=data2['date'].map(lambda x: x.replace('-','/'))
data2['gregorian_dates']=data2['date'].map(lambda x: togregorian(x))

#using the above dataframe (data2) to create a text file, containing the bills information with our own desired format 
text_file = open("inputs.txt", "w")
lines=[]
for i in data2.index:
    line="append {} {} {} {} 3 {} default {} 'nothing'".format(data2['gregorian_dates'][i].replace('-','/'),
                                                               data2['mablagh'][i],data2['daste'][i],
                                                               data2['zirdaste'][i],
                                                               ','.join(list(map(lambda x: x[2:] , eval(data2['name'][i])))),
                                                               data2['zirdaste'][i].replace('undefined',(data2['daste'][i] if (data2['daste'][i]=='elevator' or data2['daste'][i]=='parking' or data2['daste'][i]=='d') else 'e')))
    lines.append(line)
text_file.write('\n'.join(lines))
text_file.close()
    
    
    
    

#opening the text file (created before) containing all bills info 
#getting each line as a string, splitting it by spaces, and appending the created line_list one by one, to another empty list (vorudi)
k=open("inputs.txt","r")
vorudi=[]
for line in list(k.readlines()):
    line_list=list(line.split())
    vorudi.append(line_list+[line_list[2]]) #added another excessive 'mablagh' at the end, for future use


#if there exists a pre-saved data of bills from the past, the program will read it, and append the new data to it
#if not (the program is being run for the first time), an empty dictionary of bills will be created, and the new data will be appended to it
try:
    bills=dict(pd.read_csv('bills.csv'))
    for column in list(bills.keys()):
        bills[column]=list(bills[column])
except:
    bills={'vahed':[],'tarikh':[],'daste':[],'zirdaste':[], 'bedehkar':[],'sharh':[],'bestankar':[],'mande':[],'mablagh':[]}
   

#making slight changes in types of values, so they won't all be strings, and it'll get easier to use
for line in vorudi:
    line[2]=eval(str(line[2])) #the amount of money
    line[10]=eval(str(line[10])) #the excessive (copy of) amount of money
    line[5]=int(line[5]) #the responsible unit
    #if the related units (line[6]) is in form of 'x,y,z,...' , it'll be saved as a list in form of [x,y,z,...], with the units x,y,z and so on, being saved as integers (and not strings)
    #if the related units is 'all', it'll be replaced with a list of all units (available in df, the main dataframe which included basic info of building's units)
    #and if it's none of the above, then it's just one single number, and its type will only be changed from string to integer
    if type(eval(str(line[6])))==int:
        line[6]=int(line[6])
    else:
        if str(line[6])=='all':
            line[6]=[i+1 for i in range(df.shape[0])]
        else:
            line[6]=str(line[6]).split(',')
            line[6]=list(map(lambda x: int(x),line[6]))


#making a copy of vorudi list, so while making changes in vorudi, the copy (and its length) will remain untouched
raw_vorudi=vorudi[:]
x=0 #this variable will help us delete the right index of vorudi, after changes are made inside it
for line in range(0,len(raw_vorudi)):
    #if related units (raw_vorudi[line][6]) is a list of n units, it'll be splitted into n lines with the exact same info of the main line,
    #but with different values for parts indicating the related unit and it's corresponding share of the whole amount of money 
    if type(raw_vorudi[line][6])!=int:
        l=[]
        payment=raw_vorudi[line][2]
        for vahed in raw_vorudi[line][6]:
            new_line=raw_vorudi[line][:]
            new_line[6]=vahed
            RelatedUnits=raw_vorudi[line][6]
            #the dictionary below, will provide different ratios for different uses, according to the line (new_line[8]) and what category/subcategory this payment belongs to
            ratio={'parking':parking(vahed,RelatedUnits),'r':r(vahed,RelatedUnits),
                   'a':a(vahed,RelatedUnits),'e':1/len(RelatedUnits),
                   'gas':gas(vahed,RelatedUnits), 'water':water(vahed,RelatedUnits),
                   'electricity':electricity(vahed,RelatedUnits),'avarez':avarez(vahed,RelatedUnits),'elevator':elevator(vahed,RelatedUnits)}
            new_line[2]=int(np.ceil(payment*ratio[new_line[8]])) #calculating unit "vahed"'s share of money, and putting it in place of the previous amount (the whole, not-yet-distributed money)
            l.append(new_line)
        del vorudi[line+x]
        vorudi=vorudi[:line+x]+l+vorudi[line+x:] #the main line (relating to n units) is now replaced with n lines (relating to each unit), taking place in the exact same position the main line was removed from 
        x+=len(l)-1 #one line was removed and n lines were added (from/to vorudi), so all the indexes after these lines, are increased by 'n-1' 


#all the new bills info (saved in vorudi, which is a list of lists) are one by one, added to the bills dictionary, with each word of each line being appended to the place it belongs to
bills['vahed']+=[int(vorudi[x][6]) for x in range(len(vorudi))]
#before adding the dates to the list below, all 'now's are replaced with current_date, so all dates will follow the same pattern (YYYY/MM/DD)
bills['tarikh']+=list(((' '.join([vorudi[x][1] for x in range(len(vorudi))])).replace('now',current_date)).split())
bills['daste']+=[vorudi[x][3] for x in range(len(vorudi))]
bills['zirdaste']+=[vorudi[x][4] for x in range(len(vorudi))]
#the list below is a mixture of categories and subcategories, which avoids mentioning 'undefined', and instead provides what category it actually belongs to
#just so the detail of the payment (and what for it is), will be clearer to the user
bills['sharh']+=[vorudi[x][4] if vorudi[x][4]!='undefined' else vorudi[x][3] for x in range(len(vorudi))]
bills['mablagh']+=[vorudi[x][10] for x in range(len(vorudi))] #the whole not-distributed amounts of money
#if the amount of money is given as a positive number, it means that the related unit should pay the money to the responsible unit (appended to 'bedehkar')
#if the amount of money is given as a negative number, it means that the related unit has paid the money to the responsible unit (appended to 'bestankar')
bills['bedehkar']+=list(map(lambda i: i if i>=0 else 0 , [int(vorudi[x][2]) for x in range(len(vorudi))]))
bills['bestankar']+=list(map(lambda i: -i if i<0 else 0 , [int(vorudi[x][2]) for x in range(len(vorudi))]))
#the array of algerbraic sums of 'bedehkar' (as positive) and 'bestankar' (as negative) values are added as the value of a new key 'mande'
bills['mande']=np.array(bills['bedehkar'])-np.array(bills['bestankar'])
#after all the changes are made, the bills dictionary will be saved as a dataframe
bills=pd.DataFrame(bills)
#a new column 'timestamps' is added to bills dataframe, which contains the string dates of 'tarikh' column, but converted into 'timestamp' type, which makes sorting-by-dates easier
bills['timestamps']=pd.to_datetime(bills.tarikh)
bills=bills.sort_values(['vahed','timestamps','daste']).reset_index(drop=True)

output=bills #creating a copy of bills, so any furter change that will be applied to the copy won't cause any change to the main dataframe (bills)
print('برای تحویل فایل صورت حساب بازه زمانی دلخواه را وارد کنید')
baze_str=str(input('بازه زمانی: '))
if(baze_str!='-'):
    #if 'now' is entered, it'll be replaced with the current date, and then both dates of the given interval will be converted from jalali to gregorian dates
    baze=list(map(lambda x: togregorian(x),(baze_str.replace('now',tojalali(current_date))).split()))
    start=list(map(lambda x: int(x),baze[0].split('/')))
    end=list(map(lambda x: int(x),baze[1].split('/')))
    #each date string (in 'YYYY/MM/DD' format) turns into a list in format of [YYYY,MM,DD] (in which all elements are integers), all dates in form of [YYYY,MM,DD] will be saved in an array, and then the dates outside the given range will be filtered out from bills_filtered (the copy of bills dataframe)
    tarikh_array=np.array(bills['tarikh'].map(lambda x: list(map(lambda i: int(i),x.split('/'))) ))
    output=bills[tarikh_filter(tarikh_array,start,end)].reset_index(drop=True)

#output dataframe, is filtered by a few columns, some changes are made in the name of its columns, the dates are converted back to jalali dates, and it's finally saved as output.xlsx
output=output[['vahed','tarikh','daste','zirdaste','mablagh','bedehkar']]
output.columns=['vahed','date','daste','zirdaste','mablagh','sahm']
output['date']=output['date'].map(lambda x: tojalali(x))
output.to_csv('output.csv', index = False, header=True)


##the bills dataframe will be saved as a .csv file, for future use
#bills.iloc[:,:-1].to_csv('bills.csv', index = False, header=True)

#summing up all the payments for each subcategory (of 'ghabz' category)
gas=float(bills[bills['zirdaste']=='gas'].aggregate({'bedehkar':'sum'}))
water=float(bills[bills['zirdaste']=='water'].aggregate({'bedehkar':'sum'}))
electricity=float(bills[bills['zirdaste']=='electricity'].aggregate({'bedehkar':'sum'}))
avarez=float(bills[bills['zirdaste']=='avarez'].aggregate({'bedehkar':'sum'}))

#summing up all the payments for each category
ghabz=float(bills[bills['daste']=='ghabz'].aggregate({'bedehkar':'sum'}))
elevator=float(bills[bills['daste']=='elevator'].aggregate({'bedehkar':'sum'}))
parking=float(bills[bills['daste']=='parking'].aggregate({'bedehkar':'sum'}))
nezafat=float(bills[bills['daste']=='nezafat'].aggregate({'bedehkar':'sum'}))
tamirat=float(bills[bills['daste']=='tamirat'].aggregate({'bedehkar':'sum'}))
sharj=float(bills[bills['daste']=='sharj'].aggregate({'bedehkar':'sum'}))

all_pay=float(bills.aggregate({'bedehkar':'sum'})) #summing up all the payments

#dictionary containing ratios (in percentage) of each subcategory's (in 'ghabz' category) sum of payments, to the sum of all payments in this category 
nesbat_ghoboz={'gas':[str(round(float(gas/ghabz)*100,2))+'%'] , 'water':[str(round(float(water/ghabz)*100,2))+'%'],
               'electricity':[str(round(float(electricity/ghabz)*100,2))+'%'] , 'avarez':[str(round(float(avarez/ghabz)*100,2))+'%']}
#dictionary containing ratios (in percentage) of each category's sum of payments, to the sum of all payments
nesbat_koli={'ghabz':[str(round(float(ghabz/all_pay)*100,2))+'%'] , 'elevator':[str(round(float(elevator/all_pay)*100,2))+'%'],
             'parking':[str(round(float(parking/all_pay)*100,2))+'%'] , 'nezafat':[str(round(float(nezafat/all_pay)*100,2))+'%'],
             'tamirat':[str(round(float(tamirat/all_pay)*100,2))+'%'] , 'sharj':[str(round(float(sharj/all_pay)*100,2))+'%']}

#a list including each unit with its overall equity in form of [unit,equity]
pay_vahed=[[i,float(bills[bills['vahed']==i].aggregate({'mande':'sum'}))] for i in range(1,df.shape[0]+1)] 
#turning the previous list (of units with their equities) into dataframe, changing columns' names and sorting the dataframe by 'pay' column values (which contains the equities for each unit)
pay_vahed=pd.DataFrame(pay_vahed,columns=['vahed','pay']).sort_values('pay',ascending=False).reset_index(drop=True)

#printing the ratios (in form of percentage) calculated before (each subcategory to all, and each category to all)
print('سهم هزینه های هر زیرگروه از دستۀ قبض در کل هزینه های مربوط به این دسته، به شکل زیر است:')
print(pd.DataFrame(nesbat_ghoboz))
print('سهم هزینه های هر دسته نسبت به کل هزینه ها، به شکل زیر است:')
print(pd.DataFrame(nesbat_koli))


#creating a copy (of a few specific columns) of bills, so any further changes that will be applied to this copy won't cause any change to our main dataframe (bills)
bills_copy=bills[['vahed','tarikh','zirdaste','daste','bedehkar','bestankar','mande','timestamps']].sort_values('timestamps').reset_index(drop=True)
#creating a new column containg only year and month of each transaction in form of 'YYYY/MM'
bills_copy['jalali Y/M']=bills_copy['tarikh'].map(lambda x: '/'.join(tojalali(x).split('/')[:2]))
#creating two new columns which include the year and the month (separately) of each transaction 
bills_copy['jalali M']=bills_copy['jalali Y/M'].map(lambda x: int(x.split('/')[1]))
bills_copy['jalali Y']=bills_copy['jalali Y/M'].map(lambda x: int(x.split('/')[0]))

#first, a list of distinct 'YYYY/MM's is created (but only the last two elements of the list are kept in it)
#after that, the rows in which their related 'YYYY/MM' is not included in the list above, will be filtered out of bills_copy 
#finally after all the filtering is done on bills_copy, the sum of all payments (only the positive values, aka. the debts) are saved in bills_mohem
bills_mohem=float(bills_copy[bills_copy['jalali Y/M'].isin(bills_copy['jalali Y/M'].unique().tolist()[-2:]) & (bills_copy['daste']=='ghabz')].aggregate({'bedehkar':'sum'}))      
#the sum of all payments (both positive and negative values, aka equity, which were intially saved in 'mande' column) are saved in bills_mohem
vaze_koli=float(sum(bills_copy['mande']))   

#calculating the time difference between the dates of the very first and last rows of bills_copy (which was already sorted by date)
if list(bills_copy['jalali M'])[-1]-list(bills_copy['jalali M'])[0]>=0:
    zaman_y=list(bills_copy['jalali Y'])[-1]-list(bills_copy['jalali Y'])[0] 
    zaman_m=list(bills_copy['jalali M'])[-1]-list(bills_copy['jalali M'])[0]
    if zaman_y!=0:
        zaman='{} سال و {} ماه'.format(zaman_y,zaman_m)
    elif zaman_y==0:
        zaman=' ماه {} '.format(zaman_m)
elif list(bills_copy['jalali M'])[-1]-list(bills_copy['jalali M'])[0]<0:
    zaman_y=list(bills_copy['jalali Y'])[-1]-list(bills_copy['jalali Y'])[0]-1
    zaman_m=12-(list(bills_copy['jalali M'])[0]-list(bills_copy['jalali M'])[-1])
    zaman='{} سال و {} ماه'.format(zaman_y,zaman_m)
    


#printing building's status, according to all the calculations that have been done
jomle=' وضعیت این ساختمان بعد از {} از زمان اولین تراکنش به شرح زیر است'.format(zaman)
print(jomle)
while True:
    #it is considered that if the sum of debts (from the very begining to the end of dates) is less than 80% of the sum of all payments taking place in last two months (based on the provided data), the status is good
    #if it's more than 80% of the sum of all payments taking place in last two months, but still less than (100% of) it, the status is semi-good
    #and if it's more than the sum of all payments taking place in last two months, the status is bad
    if (vaze_koli)<(0.8*bills_mohem):
        print('وضعیت ساختمان مناسب است.')
        break
    elif (vaze_koli)>=(0.8*bills_mohem) and (vaze_koli)<=(bills_mohem):
        print( 'ساختمان نسبتا نامطلوب است.')
    elif (vaze_koli)>(bills_mohem):
        print( 'وضع ساختمان اضطراریست.')
    #the user will also be offered to take a look at one (or two) top units with the highest amount of unpaid debts 
    edame=input("برای اگاهی از واحد(ها) با بیشترین بدهی 'ادامه' را وارد کنید.\n")
    if edame!='خروج':
        i=len(list(pay_vahed['vahed']))
        if pay_vahed.loc[0,'pay']==pay_vahed.loc[i-1,'pay']:
            print('همه ی واحدها به یک اندازه بدهکارند')
        elif (pay_vahed.loc[1,'pay']/pay_vahed.loc[0,'pay'])<0.8:
            jomle='\nلطفا به واحد {} رجوع کنید.'.format(pay_vahed.loc[0,'vahed'])
            print(jomle)
            break
        elif pay_vahed.loc[1,'pay']>(0.8*pay_vahed.loc[0,'pay']):
            jomle='\nلطفا به واحدهای {} و {} رجوع کنید.'.format(pay_vahed.loc[0,'vahed'],pay_vahed.loc[1,'vahed'])
            print(jomle)
            break
    else:
        break



#getting the dates, units, categories and subcategories the user wants the bills to be filtered by
print("\n***فیلتر کردن***\n اطلاعات خواسته شده را وارد کنید و در صورت عدم ایجاد فیلتر در زمینه ی خواسته شده '-' را وارد کنید ")
baze_str=str(input('بازه زمانی: '))
units_str=str(input('واحدهای مورد نظر: '))
category_str=str(input('دسته(های) مورد نظر: '))
subcategory_str=str(input('زیردسته(های) مورد نظر: '))
#creating a copy of bills dataframe
bills_filtered=bills
if(baze_str!='-'):
    #if 'now' is entered, it'll be replaced with the current date, and then both dates of the given interval will be converted from jalali to gregorian dates
    baze=list(map(lambda x: togregorian(x),(baze_str.replace('now',tojalali(current_date))).split()))
    start=list(map(lambda x: int(x),baze[0].split('/')))
    end=list(map(lambda x: int(x),baze[1].split('/')))
    #each date string (in 'YYYY/MM/DD' format) turns into a list in format of [YYYY,MM,DD] (in which all elements are integers), all dates in form of [YYYY,MM,DD] will be saved in an array, and then the dates outside the given range will be filtered out from bills_filtered (the copy of bills dataframe)
    tarikh_array=np.array(bills['tarikh'].map(lambda x: list(map(lambda i: int(i),x.split('/'))) ))
    bills_filtered=bills_filtered[tarikh_filter(tarikh_array,start,end)].reset_index(drop=True)
#whichever unit,category or subcategory that is not given, will be filtered out of bills_filtered dataframe (after date-fitering has been applied to it)
if(units_str!='-'):
    units=list(map(lambda x: int(x),units_str.split(',')))
    bills_filtered=bills_filtered[bills_filtered['vahed'].isin(units)].reset_index(drop=True)
if(category_str!='-'):
    categories=category_str.split(',')
    bills_filtered=bills_filtered[bills_filtered['daste'].isin(categories)].reset_index(drop=True)
if(subcategory_str!='-'):
    subcategories=subcategory_str.split(',')
    bills_filtered=bills_filtered[bills_filtered['zirdaste'].isin(subcategories)].reset_index(drop=True)   
    
    
#reporting the financial balance according to the filtering which has been applied on the bills
first_time=1 #this variable helps to avoid printing the instruction lines, more than once
while True:
    if(first_time==1):
        print("در صورت تمایل به مشاهده تراز مالی کلی عبارت 'واحدها در کل' را وارد کنید.\nدر صورت تمایل به مشاهده تراز مالی واحدها به تفکیک شرح، عبارت 'واحد به تفکیک شرح' را وارد کنید.\nو در صورت تمایل به مشاهده تراز مالی شرح به تفکیک واحدها، عبارت 'شرح به تفکیک واحد' را وارد کنید.\nدر غیر این صورت، 'خروج' را وارد کنید.")
        first_time=0 
    showby=str(input())
    #depending on what showby is, bills_filtered will be grouped by different columns (saved in a new dataframe 'dff'), and therefore differenet sentences will be printed after
    if(showby=='واحدها در کل'):
        dff=pd.DataFrame(bills_filtered.groupby('vahed',as_index=False)['mande'].sum())
        for i in range (0,dff.shape[0]):
            if dff['mande'][i]<0:
                print('واحد '+str(dff['vahed'][i])+'، '+str(-int(dff['mande'][i]))+' تومان بستانکار است.')
            elif dff['mande'][i]==0:
                print('تراز مالی واحد '+str(dff['vahed'][i])+' صفر است.')
            else:
                print('واحد '+str(dff['vahed'][i])+'، '+str(int(dff['mande'][i]))+' تومان بدهکار است.')  
    elif (showby=='خروج'):
        break
    elif (showby=='واحد به تفکیک شرح' or showby=='شرح به تفکیک واحد'):
        if(showby=='واحد به تفکیک شرح'):
            dff=pd.DataFrame(bills_filtered.groupby(['vahed', 'sharh'])['mande'].sum().reset_index())
        elif(showby=='شرح به تفکیک واحد'):
            dff=pd.DataFrame(bills_filtered.groupby(['sharh', 'vahed'])['mande'].sum().reset_index())
        for i in range (0,dff.shape[0]):
            if(dff['mande'][i]<0):
                print('واحد '+str(dff['vahed'][i])+'، '+str(-int(dff['mande'][i]))+' تومان بابت هزینه ی '+str(dff['sharh'][i])+' '+'بستانکار است.')
            elif(dff['mande'][i]==0):
                print('تراز مالی واحد '+str(dff['vahed'][i])+' بابت هزینه ی '+str(dff['sharh'][i])+' '+' صفر است.')
            else:
                print('واحد '+str(dff['vahed'][i])+'، '+str(int(dff['mande'][i]))+' تومان بابت هزینه ی '+str(dff['sharh'][i])+' '+'بدهکار است.')



#plotting graphs, according to either units (for given units, categories and subcategories, during the given time), 
#or according to subcategories (for all units, given categories and subcategories and during the given time)
first_time=1 #this variable helps to avoid printing the instruction lines, more than once
while True:
    if(first_time==1):
        print("در صورت تمایل به مشاهده نمودار تجمعی واحدها 'واحدها'، برای مشاهده نمودار تجمعی زیردسته ها 'زیردسته ها'، و در غیر این صورت، 'خروج' را وارد کنید: ")
        first_time=0
    req=str(input())
    #depending on what req is, graphs/bar charts of the selected section(s) will be shown 
    if(req=='خروج'):
        break
    elif(req=='واحدها'): 
        #getting the dates, units, categories and subcategories the user wants the bills to be filtered by and plotted
        baze_str=str(input('بازه زمانی را وارد کنید: '))
        units_str=str(input('واحدهای مورد نظر را وارد کنید: '))
        category_str=str(input('دسته های مورد نظر را وارد کنید: '))
        subcategory_str=str(input('زیردسته های مورد نظر را وارد کنید: '))
        bills_filtered=bills #creating a copy of bills dataframe
        if(baze_str!='-'):
            #if 'now' is entered, it'll be replaced with the current date, and then both dates of the given interval will be converted from jalali to gregorian dates
            baze=list(map(lambda x: togregorian(x),(baze_str.replace('now',tojalali(current_date))).split()))
            start=list(map(lambda x: int(x),baze[0].split('/')))
            end=list(map(lambda x: int(x),baze[1].split('/')))
            #each date string (in 'YYYY/MM/DD' format) turns into a list in format of [YYYY,MM,DD] (in which all elements are integers), all dates in form of [YYYY,MM,DD] will be saved in an array, and then the dates outside the given range will be filtered out from bills_filtered (the copy of bills dataframe)
            tarikh_array=np.array(bills['tarikh'].map(lambda x: list(map(lambda i: int(i),x.split('/'))) ))
            bills_filtered=bills_filtered[tarikh_filter(tarikh_array,start,end)].reset_index(drop=True)
        #whichever unit,category or subcategory that is not given, will be filtered out of bills_filtered dataframe (after date-fitering has been applied to it)
        if(units_str!='-'):
            units=list(map(lambda x: int(x),units_str.split(',')))
            bills_filtered=bills_filtered[bills_filtered['vahed'].isin(units)].reset_index(drop=True)
        if(category_str!='-'):
            categories=category_str.split(',')
            bills_filtered=bills_filtered[bills_filtered['daste'].isin(categories)].reset_index(drop=True)
        if(subcategory_str!='-'):
           subcategories=subcategory_str.split(',')
           bills_filtered=bills_filtered[bills_filtered['zirdaste'].isin(subcategories)].reset_index(drop=True)
           
        #making sure bills_filtered dates are in correct order, before passing it on to the next (plotting) section
        bills_filtered=bills_filtered.sort_values('timestamps')
        
        #creating an empty dataframe, which will be filled with rows in which multiple transactions have occured at the same date
        duplicates_df=pd.DataFrame(columns = ['vahed', 'tarikh', 'mande','sharh'])
        for i in sorted(bills_filtered['vahed'].unique().tolist()):
            #assigning 3 columns of bills_filtered to a new dataframe 'b'
            b=bills_filtered[bills_filtered['vahed']==i][['tarikh','vahed','mande','timestamps','sharh']] 
            #creating a new column in the new dataframe, which contains cumulative sum of column 'mande'
            b['cumulative_sum']=b['mande'].cumsum()

            #creating a series of bools returning True for duplicate dates
            is_duplicate=b.duplicated(subset=['tarikh'],keep=False)
            
            #making changes in appearance: font style, font size, and figure's dimensions
            font = {'family' : 'Times New Roman', 'size' : 26}
            plt.figure(figsize = (18, 12))
            plt.rc('font', **font)
            
            #plotting a graph and a bar chart with dates (shown as jalali dates) as its x axis, and the 'cumulative_sum' column's values as its y axis
            plt.plot(b['tarikh'].map(lambda x: tojalali(x)),b['cumulative_sum'],label='cumulative sum of mablagh')
            plt.scatter(b['tarikh'].map(lambda x: tojalali(x)),b['cumulative_sum'])
            plt.bar(b['tarikh'].map(lambda x: tojalali(x)),b['mande'],label='mablagh')
            
            #making changes in appearance: rotation of x axis ticks, title of the graph, x and y labels, and legend (which was set before)
            plt.tick_params(axis="x", rotation=70)
            plt.title("unit {}".format(i))
            plt.ylabel('Toman')
            plt.xlabel('date')
            plt.legend()
            plt.show()
            
            #if the exists any duplicates, the duplicate dates (with different descriptions) will be added to the empty dataframe we created before
            if is_duplicate.sum()>0:
                duplicates_df=duplicates_df.append(b[is_duplicate][['vahed', 'tarikh','sharh', 'mande']])
        #asking if the user wants to see the details about the dates in which multiple transactions have occured
        if(duplicates_df.shape[0]!=0):
            printdup=str(input("در صورت تمایل به مشاهده ریز هزینه های تاریخ هایی که شامل چند تراکنش میشوند، 'مشاهده' را وارد کنید، و در غیر این صورت، 'خروج' را وارد کنید: "))
            if printdup=='مشاهده':
                duplicates_df['tarikh']=duplicates_df['tarikh'].map(lambda x: tojalali(x))
                print(duplicates_df.reset_index(drop=True))
    elif(req=='زیردسته ها'):
        #getting the dates and the subcategories the user wants the bills to be filtered by and plotted
        subcategory_str=input('نمودار کدام زیرگروه ها را میخواهید: ')
        baze_str=str(input('بازه زمانی را وارد کنید: '))
        bills_filtered=bills #creating a copy of bills dataframe
        if(baze_str!='-'):
            #if 'now' is entered, it'll be replaced with the current date, and then both dates of the given interval will be converted from jalali to gregorian dates
            baze=list(map(lambda x: togregorian(x),(baze_str.replace('now',current_date)).split()))
            start=list(map(lambda x: int(x),baze[0].split('/')))
            end=list(map(lambda x: int(x),baze[1].split('/')))
            #each date string (in 'YYYY/MM/DD' format) will be saved as list of integers in format of [YYYY,MM,DD], and then the dates outside the given range will be filtered out from bills_filtered (the copy of bills dataframe)
            tarikh_lists=[]
            for i in range(0,bills.shape[0]):
                tarikh_lists.append(list(map(lambda x: int(x),bills_filtered['tarikh'][i].split('/'))))
            tarikh_array=np.array(tarikh_lists)
            bills_filtered=bills_filtered[tarikh_filter(tarikh_array,start,end)].reset_index(drop=True)
        #if 'همه' is given for subcategory_str, it'll be replaced with a string including all subcategories: 'gas,water,electricity,avarez' , and then the whole subcategory_str string will be splitted into a list of the given subcatgories
        subcategories=subcategory_str.replace('همه','gas,water,electricity,avarez').split(',')
        bills_filtered=bills_filtered[bills_filtered['zirdaste'].isin(subcategories)].reset_index(drop=True)
       
        #making sure bills_filtered dates are in correct order, before passing it on to the next (plotting) section
        bills_filtered=bills_filtered.sort_values('timestamps')
    
        for j in subcategories:
            #assigning 3 columns of bills_filtered to a new dataframe 'c'
            c=bills_filtered[bills_filtered['zirdaste']==j][['tarikh','mande','timestamps','sharh']]
            #creating a new column in the new dataframe, which contains cumulative sum of column 'mande'
            c['cumulative_sum']=c['mande'].cumsum()
            
            #making changes in appearance: font style, font size, and figure's dimensions
            font = {'family':'Times New Roman' , 'size' : 26}
            plt.figure(figsize = (25, 12))
            plt.rc('font', **font)
            plt.tick_params(axis="x", rotation=70)
            
            #plotting a graph and a bar chart with dates (shown as jalali dates) as its x axis, and the 'cumulative_sum' column's values as its y axis
            plt.plot(c['tarikh'].map(lambda x: tojalali(x)),c['cumulative_sum'],label='cumulative sum of mablagh') 
            plt.scatter(c['tarikh'].map(lambda x: tojalali(x)),c['cumulative_sum'])
            plt.bar(c['tarikh'].map(lambda x: tojalali(x)),c['mande'],label='mablagh')
           
            #making changes in appearance: rotation of x axis ticks, title of the graph, x and y labels, and legend (which was set before)
            plt.ylabel('Toman')
            plt.xlabel('date')
            plt.legend()
            plt.title(j)
            plt.show()


#estimation of 'sharj' (based on the provided data from previous years) for the following year
print('شارژ واحدها در سال آتی به شرح زیر است:')
bills_est=bills[['vahed','tarikh','zirdaste','bedehkar','bestankar','mande','timestamps']].sort_values('timestamps').reset_index(drop=True)

#creating a new column containg only year and month of each transaction in form of 'YYYY/MM'
bills_est['jalali Y/M']=bills['tarikh'].map(lambda x: '/'.join(tojalali(x).split('/')[:2])) 
#creating a new column containg only the year of each transaction in form of 'YYYY'
bills_est['jalali Y']=bills_est['jalali Y/M'].map(lambda x: int(x.split('/')[0]))

#the number of distinct 'YYYY/MM's in bills_est are saved in this variable  
tedad_month=len(list(bills_est['jalali Y/M'].unique())) 

#in the follwing dataframe (allyears_pay), the sums of all payments of each unit (of all time) are grouped and saved
allyears_pay=bills_est.groupby(['vahed'],sort=True)['bedehkar'].sum().reset_index()

#the sums of all paymets for each unit during 'tedad_month' months are provided,
#so these summed up values (for each unit) will be divided by 'tedad_month' (as an average of the amount of money a unit has paid for each month), and then increased by 10%, as an estimation for the next year
allyears_pay['sharj']=(1.1*(allyears_pay['bedehkar']/tedad_month)).map(lambda x: int(np.ceil(x)))


for i in allyears_pay['vahed']:
    message='براورد شارژ واحد {0} تقریبا برابر {1} تومان است.'.format(i,allyears_pay['sharj'][i-1])
    print(message)


















