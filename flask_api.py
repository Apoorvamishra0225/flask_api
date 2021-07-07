import flask
from flask import request, jsonify
import operator
import psycopg2
app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def reccomendation():
    # Connecting to the database
    conn = psycopg2.connect(database="postgres", user="postgres",
                            password="vl2afeXGXQlmPaMPQrHM",
                            host="fireside-dev-rds-instance-1.cecnjdgxlnqo.ap-south-1.rds.amazonaws.com", port="5432")

    # fetching all the users from db
    #ghg
    cur = conn.cursor()
    cur.execute("select users.id from users ")
    temp_user_list = cur.fetchall()
    users_list = []
    for x in temp_user_list:
        users_list.append(x[0])

    # print(users_list)

    ##looping through the user list
    x = 0
    finalrec={}
    for i in users_list:
        user = i
        mutual_count = 0
        keyword_count = 0
        weightages = {}
        # print(x)
        print('user : ', user)
        # fetching the followers of the USER
        cur.execute(
            "select followers -> 'followers' from users WHERE id::text= '{}'".format(user))
        temp_followers_list = cur.fetchall()
        followers_list = []
        if temp_followers_list[0][0] != None:
            for j in range(len(temp_followers_list[0][0])):
                followers_list.append(temp_followers_list[0][0][j]['id'])
        # print('followers of users : ',followers_list)
        #
        # fetching the following list of the USER
        cur.execute(
            "select following -> 'users' from users WHERE id::text= '{}'".format(user))
        temp_following_list = cur.fetchall()
        following_list = []
        if temp_following_list[0][0] != None:
            for j in range(len(temp_following_list[0][0])):
                following_list.append(temp_following_list[0][0][j])
        # print('following of users : ',following_list)
        temp_list = [user] + followers_list + following_list
        other_users = [x for x in users_list if x not in temp_list]
        # print('other users : ',other_users)
        for k in other_users:
            other_user = k
            # print(other_user)
            user_following = following_list
            cur.execute(
                "select followers -> 'followers' from users WHERE id::text= '{}'".format(other_user))
            temp_other_user_followers_list = cur.fetchall()
            other_user_followers_list = []
            if temp_other_user_followers_list[0][0] != None:
                for j in range(len(temp_other_user_followers_list[0][0])):
                    other_user_followers_list.append(temp_other_user_followers_list[0][0][j]['id'])
            # print('followers of other user : ', other_user_followers_list)
            for j in user_following:
                if j in other_user_followers_list:
                    mutual_count = mutual_count + 1
            # print(mutual_count)
            # cur.execute(
            # "select  phone_number_with_country_code  from users WHERE id::text= '{}' and length(phone_number_with_country_code)>9".format(other_user))
            # temp_other_user_phone_number_list = cur.fetchall()
            # other_user_phone_number=[]
            # for j in range(len(temp_other_user_phone_number_list)):
            #     other_user_phone_number.append(temp_other_user_phone_number_list[j][0])
            # a=str(other_user_phone_number[0])
            # print(a)
            # from phone_iso3166.country import phone_country
            # import pycountry
            #
            # phone = a
            # c = pycountry.countries.get(alpha_2=phone_country(phone))
            # b = c.name
            # print(b)
            # cur.execute(
            #     "select  phone_number_with_country_code  from users WHERE id::text= '{}' and length(phone_number_with_country_code)9".format(user))
            # temp_user_phone_number_list = cur.fetchall()
            # user_phone_number = []
            # for j in range(len(temp_user_phone_number_list)):
            #     user_phone_number.append(temp_user_phone_number_list[j][0])
            # d = str(user_phone_number[0])
            # print(d)
            # from phone_iso3166.country import phone_country
            # import pycountry
            #
            # phone = d
            # c = pycountry.countries.get(alpha_2=phone_country(phone))
            # e = c.name
            # print(e)
            # if b==e:
            #     location=1
            # else:
            #     location=0
            cur.execute(
                "select topics  from users_topics WHERE user_id::text= '{}'".format(other_user))
            temp_other_user_interest = cur.fetchall()
            other_user_interest_temp_list = []
            other_user_interest_list = []
            for j in range(len(temp_other_user_interest)):
                other_user_interest_temp_list.append(temp_other_user_interest[0][0]['userTopics'])
                new_list = other_user_interest_temp_list[0]
                # [x for x in user_interest_temp_list[0]]
                for k in range(len(new_list)):
                    other_user_interest_list.append(new_list[k]['topic_name'])

            # print(other_user_interest_list)
            cur.execute(
                "select topics  from users_topics WHERE user_id::text= '{}'".format(user))
            temp_user_interest = cur.fetchall()
            user_interest_temp_list = []
            user_interest_list = []
            for j in range(len(temp_user_interest)):
                user_interest_temp_list.append(temp_user_interest[0][0]['userTopics'])
                new_user_list = user_interest_temp_list[0]
                # [x for x in user_interest_temp_list[0]]
                for k in range(len(new_user_list)):
                    user_interest_list.append(new_user_list[k]['topic_name'])
            # print(user_interest_list)
            for k in user_interest_list:
                if k in other_user_interest_list:
                    keyword_count = keyword_count + 1
            score = (0.4 * mutual_count) + (0.6 * keyword_count)
            weightages[other_user] = score
        cd = dict(sorted(weightages.items(), key=operator.itemgetter(1), reverse=True)[:5])
        finalrec[user]=cd
        # print(cd)

        x = x + 1

        if (x == 3):
            return jsonify(finalrec)

if __name__ == '__main__':
    app.run()

    # cd=dict(sorted(weightages.items(),key=operator.itemgetter(1),reverse=True))
    # print(cd)

    # x=x+1
    # if x==10:
    #   break

    # other_users = users - i - following - followers
    # other_users = [apoorva]
    # for j in other_users:
    #     j = apoorva
    #     user_following = list[premika]
    #     potential_followers = list[premika]
    #     for k in user_following:
    #         if k in potential_followers:
    #             mutual_count = count_mutual+1
    #     user_location = chennai
    #     potential_location = chennai
    #     if user_location == potential_location:
    #         location = 1
    #     else:
    #         location = 0
    #     if potential_active:
    #         active = 1
    #     else:
    #         active = 0
    #     user_keywords = list[interest topics from user_topics] + list[keywords from bio(NLP)] + list[clubs from clubs and rooms table]
    #     potential_keywords = list[interest topics from user_topics] + list[keywords from bio(NLP)] + list[clubs from clubs and rooms table]
    #     for k in user_keywords:
    #         if k in potential_keywords:
    #             keyword_count = keyword_count + 1
    #     score = (0.3*mutual_count) + (0.1*location) + \
    #         (0.2*active) + (0.4*keyword_count)
    #     weightages = {potentail_user: score}

    # sort weightages
    # get top 10
