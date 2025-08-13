"""
This file contains the markdown definition of the custom quote form.
"""

from src.constants import (
    HubSpotFieldType,
    HubSpotPropertyType,
    HubSpotPropertyName,
)
from src.markdown_info.custom_quote.product_fields import CUSTOM_QUOTE_FORM_PRODUCT_FIELDS

CUSTOM_QUOTE_FORM_MARKDOWN_DEFINITION = f"""
**Custom Quote Form Structure & Rules:**

The following defines the fields, requirements, and conditional logic for collecting custom quote information.
- **'Required: Yes'**: This information must be asked and should be provided by the user.
- **'Required: No'**: This information is optional. If the user provides this information, you can store it, but you don't explicitly ask for it unless specified in a Guidance Note.
- **'Conditional Logic'**: Describes when a field becomes relevant or required based on previous answers.
- **'List values'**: For Dropdown fields, these are the exact, fixed options the user must choose from.
- **'PQA Guidance Note'**: Specific instructions for the Price Quote Agent on how to guide the Planner for this field.

**I. Product Information (Step 1)**
*(PQA starts here to identify the product)*

{CUSTOM_QUOTE_FORM_PRODUCT_FIELDS}

---
### Products Requiring No Additional Options
If the user selects one of the following Product Categories, do not ask for Format or Finish. Proceed directly to **II. Quote Information**.
- **Badges**
- **Patches**

**II. Quote Information (Step 2)**
*(PQA collects size and quantity after product is identified)*
33. **Display Label:** Total Quantity:
    - **HubSpot Internal Name:** `{HubSpotPropertyName.TOTAL_QUANTITY.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.NUMBER.value}
    - **Required:** Yes
    - **PQA Guidance Note:** Ask "What is the total quantity you are looking for?".
34. **Display Label:** Dimensions
    - **HubSpot Internal Name:** `{HubSpotPropertyName.WIDTH_IN_INCHES.value}`, `{HubSpotPropertyName.HEIGHT_IN_INCHES.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.NUMBER.value}
    - **Required:** Yes
    - **PQA Guidance Note:** Ask for dimensions in a single question: "What are the dimensions for your product (e.g., '3x3 inches')?". The PQA will parse the user's response for width and height values.

**III. Contact Information (Step 3)**
*(PQA collects the single point of contact)*
35. **Display Label:** Email
    - **HubSpot Internal Name:** `{HubSpotPropertyName.EMAIL.value}`
    - **Property Type:** {HubSpotPropertyType.CONTACT_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.SINGLE_LINE_TEXT.value}
    - **Required:** No (but one of email or phone is required)
    - **PQA Guidance Note:** Ask a single, clear question: "Perfect. And how can our team contact you with your quote? Please provide an email address or a phone number.".
36. **Display Label:** Phone number
    - **HubSpot Internal Name:** `{HubSpotPropertyName.PHONE.value}`
    - **Property Type:** {HubSpotPropertyType.CONTACT_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.PHONE_NUMBER.value}
    - **Required:** No (but one of email or phone is required)
    - **Limits:** Must be between 7 and 20 characters.
    - **PQA Guidance Note:** This is collected via the same question as the email.

**IV. Final Confirmation Question (Step 4)**
*(The very last question)*
37. **Display Label:** Are you a promotional product distributor?
    - **HubSpot Internal Name:** `{HubSpotPropertyName.PROMOTIONAL_PRODUCT_DISTRIBUTOR.value}`
    - **Property Type:** {HubSpotPropertyType.TICKET_PROPERTY.value}
    - **Field Type:** {HubSpotFieldType.SINGLE_CHECKBOX.value}
    - **Required:** No
    - **PQA Guidance Note:** Ask this as the final question: "Got it. One last thing: to make sure we get you to the right team, are you a promotional product distributor?".

**V. Optional & Context-Populated Fields**
*(These fields are not asked for directly. The PQA should parse the user's conversation and populate these fields if the user provides the information voluntarily.)*
38. **Display Label:** First name
    - **HubSpot Internal Name:** `{HubSpotPropertyName.FIRSTNAME.value}`
    - **Required:** No
    - **PQA Guidance Note:** Do not ask for this. Populate only if the user offers it.
39. **Display Label:** Last name
    - **HubSpot Internal Name:** `{HubSpotPropertyName.LASTNAME.value}`
    - **Required:** No
    - **PQA Guidance Note:** Do not ask for this. Populate only if the user offers it.
40. **Display Label:** Upload your design
    - **HubSpot Internal Name:** `{HubSpotPropertyName.UPLOAD_YOUR_DESIGN.value}`
    - **Required:** No
    - **PQA Guidance Note:** Do not ask for this. The Planner will prompt the user for a file after the ticket is created. If a file is uploaded during the conversation, this field can be noted as 'File Provided'.
41. **Display Label:** Additional Instructions:
    - **HubSpot Internal Name:** `{HubSpotPropertyName.ADDITIONAL_INSTRUCTIONS.value}`
    - **Required:** No
    - **PQA Guidance Note:** Do not ask for this directly. This field is a catch-all for any extra details the user provides during the conversation.

**VI. System Generated Fields (For AI agents internal use only):**
- **HubSpot Internal Name:** `{HubSpotPropertyName.SUBJECT.value}`
- **HubSpot Internal Name:** `{HubSpotPropertyName.CONTENT.value}`
- **HubSpot Internal Name:** `{HubSpotPropertyName.TYPE_OF_TICKET.value}`
"""
