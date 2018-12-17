from facebook_business.api import FacebookAdsApi

import datetime
import Campaign
import Database
import time

access_token = 'EAAcMozUtPNEBAHam4CbXXFFdL3ZCnl1ercnUymaGdSxAx4j3TZBe1TeSJRb7HfjZBJQxPpkLaFiNvYPjvaH3NJHZAHuHXDsPA8j01aUAYjziceopNodDZCbZAnfX03WGgF7fJynv6qZAfiZBLTcgNUQOE5IU67G38aHyIZBzZAcGPoqfQ0fCXZAA7dptEKeBTOHbkZC0kZA4RhQotoQZDZD'
add_account_id = 'act_2060977594232185'
page_id = '241279066555171'
app_id = '558905831213477'


FacebookAdsApi.init(access_token=access_token)

#Create campaign
campaignId = "23843110047550212"

budget = 100
bidAmount = 0

con = Database.getConnection('localhost123', 'sa', 'P@ssw0rd', 'GH.Warehouse')#

offerCodeList = Database.getOfferCodes(con, 'jb4', 'Retention')#

today = datetime.date.today()
offercodeCounter = 0
for row in offerCodeList:
    offercodeCounter += 1
    code = row[0]
    mobileNoList = Database.getMobilenumbers(con, 'jb4', 'Retention', code)#
    mobileNoCount = len(mobileNoList)
    
    scheduleStartTime = datetime.date.today()
    scheduleEndTime = None
    
    customerAudienceArr = []

    if len(mobileNoList) < 10000 :
        mobileNoArr = []
        i = 0
        for no in mobileNoList:
            if(i == 0):
                offerValidity = no[4]
                scheduleEndTime = str(today + datetime.timedelta(days=offerValidity))
            mobileNoArr.append(str(no[1]))
            i += 1

        uniqueName = str(code).strip() + ':' + str(scheduleStartTime) + ':' + str(scheduleEndTime)

        print("Started creating ad " + str(offercodeCounter) + ' name: ' + uniqueName)
        Database.initLog(con, code, campaignId, scheduleStartTime, scheduleEndTime, uniqueName, mobileNoCount)
    
        CustomAudienceId = Campaign.createCustomizeAudiance(add_account_id, uniqueName, mobileNoArr)
        customerAudienceArr.append(CustomAudienceId)
        Database.customizeAudianceLog(con, uniqueName, CustomAudienceId)
        time.sleep(60)
    else :
        i = 1
        dividedArr = list(Campaign.chunk(mobileNoList, 10000))
        mobileNoArr = []
        for no in dividedArr:
            for mob in no :
                if(i == 1):
                    offerValidity = mob[4]
                    scheduleEndTime = str(today + datetime.timedelta(days=offerValidity))
                mobileNoArr.append(str(mob[1]))
            uniqueName = str(code).strip() + ':' + str(scheduleStartTime) + ':' + str(scheduleEndTime) 
            uniqueAdName = uniqueName + str(i) 

            print("Started creating ad " + str(offercodeCounter) + ' name: ' + uniqueName)
            Database.initLog(con, code, campaignId, scheduleStartTime, scheduleEndTime, uniqueName, mobileNoCount)
            CustomAudienceId = Campaign.createCustomizeAudiance(add_account_id, uniqueAdName, mobileNoArr)
            mobileNoArr = []
            customerAudienceArr.append(CustomAudienceId)
            #Database.customizeAudianceLog(con, uniqueName, CustomAudienceId)
            time.sleep(120)
            i += 1

    adSetId = Campaign.createAddSet(add_account_id, campaignId, customerAudienceArr, uniqueName, budget, bidAmount, scheduleStartTime, scheduleEndTime)
    Database.addSetCreateLog(con, uniqueName, adSetId)
    
    image_url = 'dont_cook_tuesdays.jpg'
    messageBody = 'Come and redeem your coupon from the closest Pizzahut outlet or order online. (Please refer to the coupon code sent via SMS)'
    link = 'https://www.pizzahut.lk/'

    hashimage = Campaign.createImage(add_account_id, image_url)

    adId = Campaign.createAdd(add_account_id, adSetId, page_id, uniqueName, messageBody, hashimage, link)
    Database.addCreateLog(con, uniqueName, adId)

    print("End creating ad " + str(offercodeCounter) + ' name: ' + uniqueName)
    
    time.sleep(180)

con.close()
    

