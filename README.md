# Presentation
You can use this code to generate your monthly rental receipt for your tenants.
It will : 
- Generate a new file on Google Drive on a specific folder
- Fill all fields dependending on which value you give to it
- Compute the price without charges knowing full fee and rental charges (not yet configurable)
- Send email to your tenant and a copy to you

# How to use ? 

1. Create a folder on your Google Drive with a template receipt. It should contain the following fields : 
    - `{{period}}`
    - `{{monthly-fee}}`
    - `{{rental-charge}}`
    - `{{monthly-total}}`
    - `{{today-date}}`
2. Copy somewhere the `id` of this file (have a look in navigation bar)
3. Clone the repository on your computer
4. Open your terminal, go in the project and `pip install .`
5. Go to `quittances/edit.py` and change here the values for rental fees and rental charges
6. In the Makefile, create another step remplacing values. The `TEMPLATE ID` should be the id of the template from step one
7. Follow the instructions here for the Google part https://developers.google.com/docs/api/quickstart/python
8. Then, in your terminal in the project call `make example`
