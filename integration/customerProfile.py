# integration/CustomerProfile.py

class CustomerProfile:

    def getCustomerProfile(self, msisdn: str) -> dict:
        """
        Returns static customer profile for now.
        Later: replace with real API call.
        
        Request Body: { "phoneNo": 923001234567 }
        Response: 200 OK with customer details
        """
        #print(f"📋 Fetching customer profile for: {msisdn}")

        # Static response for now
        return {
            "customerId": 101,
            "customer_name": "John Doe",
            "phone1": msisdn,
            "customer_address": "G-8, Islamabad"
        }

    def checkAvailableLocation(self, customer_address: str):
        """
        Checks if delivery is available at the given address.
        No implementation yet.
        """
        #print(f"📍 Checking delivery availability for: {customer_address}")
        exit()