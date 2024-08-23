# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from botbuilder.schema import CardAction, HeroCard, Mention, ConversationParameters, Attachment, Activity, ActivityTypes, ConversationReference
from botbuilder.schema._connector_client_enums import ActionTypes
from botbuilder.core import ActivityHandler, CardFactory, TurnContext, MessageFactory, BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import ChannelAccount
from langchain_flow import Agents
from memory_management import Memory_Management

class MyBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        Agent_obj = Agents()
        query = turn_context.activity.text
        check_id = turn_context.activity.from_property.__dict__["id"]
        name = turn_context.activity.from_property.__dict__["name"]
        if check_id not in Memory_Management.user_id_list:
            to_send = f"Hey {name}. You are not authorized to access United-Wings-v2(Teams Conversation Bot).<br>Please contact IT Admin for any help."
            await turn_context.send_activity(to_send)
            return
        elif query in ["confirm", "deny"]:
            await self.handle_response(turn_context, check_id, name)
            return
        else:   
            try:
                response = int(Agent_obj.Response(query))
                if response == 1:
                    User_ID, response = Memory_Management.get_response(query, response)
                    if User_ID in Memory_Management.db:
                        to_send = f"A request is in process for user id: {User_ID}. Please wait {name}."
                        await turn_context.send_activity(to_send)
                        return
                    Action = response["Action"]
                    Data = response["Data"]
                    button = [
                    CardAction(type=ActionTypes.message_back, title="Confirm", text="confirm", value={"Action": Action, "Data": Data, "User_ID": User_ID, "Selected": "confirm"}),
                    CardAction(type=ActionTypes.message_back, title="Deny", text="deny", value={"Action": Action, "Data": Data, "User_ID": User_ID, "Selected": "deny"})]
                    card = HeroCard(title="Final Verification", text=f"Action : {Action} <br> Data : {Data} <br> User_ID : {User_ID}", buttons=button)
                    sent_activity =  await turn_context.send_activity(MessageFactory.attachment(CardFactory.hero_card(card)))
                    message_id = sent_activity.id
                    Memory_Management.store_db(User_ID, response, message_id, name, check_id, query)
                    
                elif response == 2:
                    to_send = f"Please ask queries related to United Airlines Database {name}"
                    await turn_context.send_activity(to_send)
                    return
                    
            except Exception as e:
                to_send = "The bot encountered an agent error or bug. To continue to run this bot, please fix the bot source code."
                await turn_context.send_activity(to_send)
                return
                
        
    async def handle_response(self, turn_context: TurnContext, check_id, name):
        if turn_context.activity.text in ["confirm", "deny"]:
            selected_option = "Confirm" if turn_context.activity.text == "confirm" else "Deny"
            try:
                user_id = turn_context.activity.value['User_ID']
                check_id2 = Memory_Management.get_data(user_id)["check_id"]
                if check_id == check_id2:
                    new_card = HeroCard(title="Final Verification",text=f"Action: {turn_context.activity.value['Action']} <br> Data: {turn_context.activity.value['Data']} <br> User_ID: {turn_context.activity.value['User_ID']} <br> You selected: {selected_option}", buttons=[])
                    await turn_context.send_activity(
                        MessageFactory.attachment(CardFactory.hero_card(new_card))
                    )
                    message_id = Memory_Management.get_data(user_id)["Message_id"]
                    await turn_context.delete_activity(message_id)
                else:
                    name2=Memory_Management.get_data(user_id)["name"] 
                    to_send = f"NOTE: This message is for {name}.<br> Hey {name}. The request was raised by {name2}. If you need any help or have questions, please let me know."
                    await turn_context.send_activity(to_send)
                    return                
                
                if turn_context.activity.text == "confirm":
                    name=Memory_Management.get_data(user_id)["name"]
                    query = Memory_Management.get_data(user_id)["query"]
                    to_send = f'Your request for the query,<br>"{query}"<br> has been initiated successfully {name}.'
                    await turn_context.send_activity(to_send)                
                
                elif turn_context.activity.text == "deny":
                    name=Memory_Management.get_data(user_id)["name"]
                    to_send = f"It seems you’ve decided not to continue {name}. If you need any help or have questions, <br> please let me know with more details."
                    Memory_Management.del_data(user_id)
                    await turn_context.send_activity(to_send)
            except Exception as e:
                to_send = "The bot encountered an agent error or bug. To continue to run this bot, please fix the bot source code."
                await turn_context.send_activity(to_send)

    async def on_members_added_activity(
        self,
        members_added: ChannelAccount,
        turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello and welcome!")
                
  