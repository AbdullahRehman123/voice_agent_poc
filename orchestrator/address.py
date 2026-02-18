# orchestrator/address.py

from ai import STT, LLM, TTS
from integration.routeToAgent import RouteToAgent
from integration.customerProfile import CustomerProfile


class AddressOrchestrator:
    """
    Handles collecting and validating the delivery address.
    """

    def __init__(self, logger=None):
        self.logger = logger
        self.stt = STT(logger=logger)
        self.llm = LLM(logger=logger)
        self.tts = TTS(logger=logger)
        self.router = RouteToAgent()
        self.customer_profile_service = CustomerProfile()
    
    async def execute(self, context: dict) -> bool:
        """
        Full address flow:
        1. Fetch customer profile using msisdn from context
        2. Confirm address with customer
        3. Validate response (yes/no/others)
        4. On yes: sayThanks + checkAvailableLocation
        5. On no: ask for address, validate with LLM, retry once if invalid, then route to agent if still invalid
        6. On others: retry once, then route to agent
        """
    
        msisdn = context.get("msisdn")

        # ── Step 1: Fetch customer profile ──────────────────────────────
        if self.logger:
            self.logger.info(f"Address - Fetching customer profile for msisdn: {msisdn}")
        
        profile = self.customer_profile_service.getCustomerProfile(msisdn)
        context["customer_profile"] = profile

        customer_name = profile.get("customer_name", "")
        customer_address = profile.get("customer_address", "")

        if self.logger:
            self.logger.info(f"Address - Profile fetched: {profile}")

        # ── Step 2: Build and ask address confirmation question ──────────
        address_question = (
            f"Meri baat {customer_name} se ho rahi hai. "
            f"Aap ka address {customer_address} hai, "
            f"kya aap isi address par delivery karwana chahtay hain?"
        )

        await self.tts.play_audio(address_question)
        if self.logger:
            self.logger.info(f"Address - Asked: {address_question}")

        # Capture response
        user_response = await self.stt.transcribe()
        print(f"📝 Address (Urdu): {user_response[::-1]}")
        if self.logger:
            self.logger.info(f"Address - User response: {user_response}")

        # ── Step 4: Check intent with LLM ────────────────────────────────
        intent = await self._check_address_intent(address_question, user_response)
        #intent = "no"  # Hardcoded for now

        if self.logger:
            self.logger.info(f"Address - Intent (attempt 1): {intent}")

        # ── Step 5: Handle intent ────────────────────────────────────────
        if intent == "yes":
            await self._say_thanks_and_check_location(customer_address, context)
            return True

        elif intent == "no":
            # if self.logger:
            #     self.logger.info("Address - User declined address, routing to agent")
            # farewell = "Main aap ko staff se connect kar raha hoon jo aap ki help kar sakta hai. Kindly line per rahein."
            # await self.tts.play_audio(farewell)
            # await self.router.routeCallToAgent()
            # return False

            # no or others on second attempt → ask for new address
            return await self._collect_new_address(context)           

        else:  # others
            result = await self._get_response_on_others(
                address_question, context, customer_address
            )
            return result
        
    async def _check_address_intent(self, address_question: str, user_response: str) -> str:
        """
        Check user response against address confirmation question.
        Returns: yes, no, or others
        """
        prompt = (
            f"Classify this customer response against question [{address_question}] "
            f"as 'yes', 'no' or 'others' to confirm address: \"{user_response}\" "
            f"Reply only with: yes, no or others"
        )

        if self.logger:
            self.logger.info(f"Address - Sending to LLM for intent check: {user_response}")

        response = await self.llm.get_response(prompt, temperature=0.0)
        result = response.lower().strip()

        if self.logger:
            self.logger.info(f"Address - LLM intent result: {result}")

        if "yes" in result:
            return "yes"
        elif "no" in result:
            return "no"
        else:
            return "others"

    async def _get_response_on_others(
        self,
        address_question: str,
        context: dict,
        customer_address: str
    ) -> bool:
        """
        Called when first response was 'others'.
        Retries once with apology + original question.
        """
        retry_message = f"Sorry, main aapki baat theek se sun nahi paaya. {address_question}"
        await self.tts.play_audio(retry_message)

        if self.logger:
            self.logger.info("Address - Retrying after 'others' response")

        # Capture retry response
        user_response_retry = await self.stt.transcribe()
        print(f"📝 User response (retry): {user_response_retry[::-1]}")
        if self.logger:
            self.logger.info(f"Address - User response (attempt 2): {user_response_retry}")

        # Check intent again
        intent = await self._check_address_intent(address_question, user_response_retry)
        #intent = "yes"  # Hardcoded for now
        if self.logger:
            self.logger.info(f"Address - Intent (attempt 2): {intent}")

        if intent == "yes":
            await self._say_thanks_and_check_location(customer_address, context)
            return True
        else:
            # no or others on second attempt → route to agent
            # if self.logger:
            #     self.logger.info(f"Address - Intent '{intent}' on retry, routing to agent")
            # farewell = "Main aap ko staff se connect kar raha hoon jo aap ki help kar sakta hai. Kindly line per rahein."
            # await self.tts.play_audio(farewell)
            # await self.router.routeCallToAgent()
            # return False

            # no or others on second attempt → ask for new address
            return await self._collect_new_address(context)        
                
    async def _collect_new_address(self, context: dict) -> bool:
        """
        Ask user to provide new address with 1 retry.
        Returns True if valid address collected, False if need to route to agent.
        """
        question = "Apna address bataen?"
        await self.tts.play_audio(question)

        if self.logger:
            self.logger.info("Address - Asking user for address")
        
        # First attempt
        user_address_response = await self.stt.transcribe()
        print(f"📝 Address: {user_address_response[::-1]}")
        if self.logger:
            self.logger.info(f"Address - User provided: {user_address_response}")
        
        reformatted_address = await self._reformat_address(user_address_response)
        
        if reformatted_address and reformatted_address != "NOT_AN_ADDRESS":
            # Valid address
            context["address"] = reformatted_address
            print(f"✅ Reformatted Address: {reformatted_address}")
            if self.logger:
                self.logger.info(f"Address - Reformatted successfully: {reformatted_address}")
            return True
        
        # Invalid address - retry once
        if self.logger:
            self.logger.warning(f"Address - LLM returned NOT_AN_ADDRESS for: {user_address_response}, retrying")
        
        retry_message = "Address ko samajhne mein problem hui. Address doobara bataen."
        await self.tts.play_audio(retry_message)
        
        # Second attempt
        address_response_retry = await self.stt.transcribe()
        print(f"📝 Address (retry): {address_response_retry[::-1]}")
        if self.logger:
            self.logger.info(f"Address - Retry user response: {address_response_retry}")
        
        reformatted_address = await self._reformat_address(address_response_retry)
        
        if reformatted_address and reformatted_address != "NOT_AN_ADDRESS":
            context["address"] = reformatted_address
            print(f"✅ Reformatted Address: {reformatted_address}")
            if self.logger:
                self.logger.info(f"Address - Retry reformatted successfully: {reformatted_address}")
            return True
        
        # Still invalid after retry - route to agent
        print("❌ Could not understand address after retry")
        if self.logger:
            self.logger.error(f"Address - Could not understand address after retry, routing to agent")
        
        farewell = "Main aap ko staff se connect kar raha hoon jo aap ki help kar sakta hai. Kindly line per rahein."
        await self.tts.play_audio(farewell)
        await self.router.routeCallToAgent()
        
        return False

    async def _say_thanks_and_check_location(self, customer_address: str, context: dict):
        """
        Called on confirmed yes.
        Says thank you then checks delivery availability.
        """
        await self.tts.play_audio("Shukria, Kindly wait karien.")
        if self.logger:
            self.logger.info("Address - Said thanks, checking available location")

        context["address"] = customer_address

        # Check delivery availability (exits internally for now)
        self.customer_profile_service.checkAvailableLocation(customer_address)

    async def _reformat_address(self, urdu_address: str) -> str:
        """
        Reformat Urdu address to English format using LLM.
        
        Args:
            urdu_address: The address in Urdu
        
        Returns:
            str: Reformatted address in English or "NOT_AN_ADDRESS"
        """
        if self.logger:
            self.logger.info(f"Address - Sending to LLM for reformatting: {urdu_address}")
        
        prompt = f"""Convert this Urdu text to English address format if it contains an address:
"{urdu_address}"

Rules:
- If the text is NOT an address, return: "NOT_AN_ADDRESS"
- If it is an address:
  • Transcribe EXACTLY what is spoken - do not add or invent words
  • Convert all numbers to English numerals (1, 2, 3...)
  • Replace: مکان/مکان نمبر/ہاؤس نمبر → House Number or H#
  • Replace: گلی/گلی نمبر → Street Number or Street #
  • Replace: بلاک → Block
  • Keep location names in readable English
  • Output format: House Number [#], [Block Name] Block, [Area], [City]

Output only the reformatted address or "NOT_AN_ADDRESS". Do not add extra words."""
        
        response = await self.llm.get_response(prompt, temperature=0.0)
        result = response.strip()

        if self.logger:
            self.logger.info(f"Address - LLM reformat result: {result}")

        return result