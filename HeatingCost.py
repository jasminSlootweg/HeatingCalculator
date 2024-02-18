# This is a project for ElleHacks 2024, a calculator and suggestion tool to help low-income families manage their heating costs in the Winter.
# This app will calculate the users' current spending, and potential spending based on suggestions the code will offer to lower their costs.
# NOTE THAT THIS IS A ROUGH ESTIMATE BASED ON A LOT OF AVERAGE VALUES FOR r-VALUE CALCULATIONA S WELL AS COST CALCULATION
# Global Variables
sqft = 0
indoorTemp = 0
averageOutdoorTemp = 0
insulationFactor = 0
hoursPerDay = 0
pricePlan = 0
gas_or_electric = 0
kilowatts = 0
totalCost = 0
cubicmeters = 0
deliveryCost = 0
walls = None
windows = None
doors = None
floorsInsulated = False


# Get basic user information to determine if we need more diagnostic steps
def get_user_information():
    global sqft, indoorTemp, averageOutdoorTemp, insulationFactor, hoursPerDay, pricePlan, gas_or_electric, kilowatts, cubicmeters

    sqft = float(input("What is the square footage of your home: "))
    indoorTemp = float(input("What is your desired indoor temperature in Celsius: "))
    averageOutdoorTemp = float(input("What is the average outdoor temperature in Celsius: "))
    gas_or_electric = float(input("Does your home run on electric(1) or gas(0): "))
    insulationFactor = float(input("What is your insulation factor? If you don't know, enter 0: "))

    # If the user does not know their insulation factor, calculate it for them
    if insulationFactor == 0:
        insulationFactor = calculate_rvalue()

    # After getting all the above information, we can now calculate BTUs per hour, or British Thermal units
    btu = calculate_btu()

    #calculate Cost
    if(gas_or_electric == 1):
        #Convert BTU to Kilowatts
        kilowatts = btu_to_kilowatts(btu)
        calculate_electric_cost()
        print("Your total cost for heating is ", totalCost)
    else:
        cubicmeters = btu_to_cubic_meters(btu)
        calculate_gas_cost()
        print("Your total cost for heating is ", totalCost)

    give_suggestions()

# When the user does not know their insulation factor, calculate it for them (insulation factor is average R-value)
def calculate_rvalue():
    knowsValue = 'no'
    components = ['walls', 'floors', 'windows', 'doors']
    componentData = {}
    totalArea = 0
    while True:
        knowsValue = input("Do you know the R-Values of your home (yes or no): ").lower()
        if knowsValue != 'no' and knowsValue != 'yes':
            print("Not a valid response. Please enter yes or no")
            continue
        elif knowsValue == 'yes':
            # Ask for R value of specific parts of the home
            for component in components:
                area = float(input(f"Enter the total area of the {component} in square feet: "))
                r_value = float(input(f"Enter the average R-value of the {component}: "))

                componentData[component] = {'area': area, 'r_value': r_value}
                totalArea += area

            # Calculate weighted average R-value
            rValueSum = sum(data['area'] * data['r_value'] for data in componentData.values())
            averageRvalue = rValueSum / totalArea if totalArea > 0 else 0
            print("Your average R value is " + "{:.2f}".format(averageRvalue))
            return averageRvalue
        else:
            # If the user does not know the R-values of their home, then guide them through the estimation process
            for component in components:
                area = float(input(f"Enter the total area of the {component} in square feet: "))
                r_value = get_estimated_r_value(component)  # Call the estimation function here

                componentData[component] = {'area': area, 'r_value': r_value}
                totalArea += area

            # Calculate weighted average R-value
            rValueSum = sum(data['area'] * data['r_value'] for data in componentData.values())
            averageRvalue = rValueSum / totalArea if totalArea > 0 else 0
            print("Your average R value is " + "{:.2f}".format(averageRvalue))
            return averageRvalue

#If the user does not know the R-value of their home components, we will ask for the materials
#of their home and return the average R-value for that component
def get_estimated_r_value(component):
    if component == 'walls':
        walls = input("Enter the type of wall construction (wood frame, brick, concrete block, etc.): ").lower()
        if 'wood' in walls:
            return 13  # Typical R-value for wood frame with insulation
        elif 'brick' in walls:
            return 10  # Estimated R-value for brick walls
        elif 'concrete' in walls:
            return 8  # Estimated R-value for concrete block walls
        else:
            return 5  # Default or unknown wall type
    elif component == 'floors':
        floors = input("Is there insulation under the floor (yes/no)? ").lower()
        if floors == 'yes':
            floorsInsulated = True
            return 19  # Typical R-value for insulated floors
        else:
            return 2  # Estimated R-value for uninsulated floors
    elif component == 'windows':
        windows = input("Enter the type of windows (single, double, triple-pane): ").lower()
        if 'single' in windows:
            return 1  # Estimated R-value for single-pane windows
        elif 'double' in windows:
            return 2  # Estimated R-value for double-pane windows
        elif 'triple' in windows:
            return 3  # Estimated R-value for triple-pane windows
        else:
            return 2  # Default for unknown window type
    elif component == 'doors':
        doors = input("Enter the door material (wood, metal, insulated): ").lower()
        if 'wood' in doors:
            return 3  # Average R-value for wood doors
        elif 'metal' in doors:
            return 5  # Average R-value for metal doors
        elif 'insulated' in doors:
            return 7  # if doors are specially insulated
        else:
            return 3  # Default for unknown door type
    else:
        return 1  # just-in-case R-value

#This function takes the information the user gives of their home, and calculates the British Thermal Units needed to heat their home
def rvalue_to_insulation_effect(averageRvalue):
    if averageRvalue > 0:
        return 1 / averageRvalue
    else:
        return 1  #default
    
def calculate_btu():
    global sqft, indoorTemp, averageOutdoorTemp, insulationFactor

    # Convert temperatures from Celsius to Fahrenheit
    indoorTemp_F = (indoorTemp * 9/5) + 32
    averageOutdoorTemp_F = (averageOutdoorTemp * 9/5) + 32

    # Calculate the temperature difference in Fahrenheit
    temperature_difference = indoorTemp_F - averageOutdoorTemp_F

    insulationEffect = rvalue_to_insulation_effect(insulationFactor)

    btu_required = sqft * temperature_difference * insulationEffect
    print(f"Estimated BTUs required to heat your home: {btu_required:.2f}")
    return btu_required

#For electricity
def btu_to_kilowatts(btu):
    return btu*0.000293

#For gas
def btu_to_cubic_meters(btu):
    # Energy content of natural gas in BTUs per cubic meter (approximate value)
    btu_per_cubic_meter = 35300
    
    # Convert BTU to cubic meters
    cubic_meters = btu / btu_per_cubic_meter
    return cubic_meters

#THIS IS ONLY DATA FOR THE COMPANY HYDRO ONE, didnt have enough time to do costs for other companies
def calculate_electric_cost():
    global pricePlan, kilowatts, totalCost
    pricePlan = float(input("What is your price plan? Time of use (1), Ultra-Low-Overnight (2), or Tiered (3). Please enter 1, 2, or 3: "))
    
    #Price formulas are based on the default percentages for off, mid, and on peak usage
    if(pricePlan == 1):
        #Price plan one is TOU, or Time Of Use
        offPeak = kilowatts*0.63*0.087 #X*0.63*0.087
        midPeak = kilowatts*0.18*0.122 #X*0.18*0.122
        onPeak = kilowatts*0.19*0.182 #X*0.19*0.182
        wattCost = offPeak + midPeak + onPeak
    elif(pricePlan == 2):
        #Price pkan two is ULO, or Ultra-Low-Overnight 
        offPeak = kilowatts*0.23*0.087 # X*0.23*0.087
        midPeak = kilowatts*0.331*0.122 # X*0.331*0.122
        onPeak = kilowatts*0.179*0.286 # X*0.179*0.286
        ultraLow = kilowatts*0.26*0.028 # X*0.26*0.028
        wattCost = offPeak + midPeak + onPeak + ultraLow
    elif(pricePlan == 3):
        if(kilowatts < 1000):
            wattCost = kilowatts*0.103
        else:
            wattCost = 103+(kilowatts-1000)*0.125

    print("What is your Residential Area? \n1)AR Residential & UR Residential\n2)AUR Residential\n3)R1 Residential\n4)R2 Residential\n5)Former Orillia Power Distribution Corporation Service Area\n6)Former Peterborough Distribution Inc. Service Are")
    residential = float(input("Please enter 1,2,3,4,5 or 6: "))
    if(residential == 1):
        #AR Residential & UR Residential
        deliveryCost = 40+0.42+0.11+kilowatts*0.0007+kilowatts*0.0009+kilowatts*0.0126+kilowatts*0.0093
    elif(residential == 2):
        #AUR Residential
        deliveryCost = 32.63+0.42+0.11+kilowatts*0.0007+kilowatts*0.0009+kilowatts*0.0126+kilowatts*0.0093
    elif(residential == 3):
        #R1 Residential
        deliveryCost = 43+0.42+0.11+kilowatts*0.0007+kilowatts*0.0009+kilowatts*0.0126+kilowatts*0.0093
    elif(residential == 4):
        #R2 Residential
        deliveryCost = 44+0.42+0.11+kilowatts*0.0007+kilowatts*0.0009+kilowatts*0.0126+kilowatts*0.0093
    elif(residential == 5):
        #Former Orillia Power Distribution Corporation Service Area
        deliveryCost = 33.93+2.56+0.42+0.28+kilowatts*0.0006+kilowatts*0.0098+kilowatts*0.0077
    elif(residential == 6):
        #Former Peterborough Distribution Inc. Service Are
        deliveryCost = 26.39+0.42+kilowatts*0.0001+kilowatts*0.0079+kilowatts*0.01+1.0548+0.23

    regulatoryCharges = kilowatts*0.0041+kilowatts*0.0014+kilowatts*0.0004+0.25

    totalCost = (wattCost + deliveryCost + regulatoryCharges) * 1.13

def calculate_gas_cost():
    global totalCost, cubicmeters, deliveryCost
    region = float(input("What is your zone?\n1)Enbridge Gas Inc. Union South Rate Zone\n2)Enbridge Gas Inc. Union North East Rate Zone\n3)Enbridge Gas Inc. ​​Union North West Rate Zone\n4)Enbridge Gas Inc.\nPlease enter 1,2,3 or 4: "))
    if(region == 1):
        totalCost = 23.98 #Customer base charge
        if (cubicmeters <= 100 ):
            deliveryCost =  cubicmeters * 0.073842
        elif (cubicmeters > 100 & cubicmeters <= 250):
            deliveryCost = (100 * 0.073842) + ((cubicmeters-100) * 0.070718)
        elif(cubicmeters > 250):
            deliveryCost = (100 * 0.073842) + (150 * 0.070718) + ((cubicmeters-250) * 0.062653)
        federalTax = cubicmeters * 0.1239 #Federal Carbon charge
        gasSupplyCharge =  cubicmeters * 0.192506

        totalCost += deliveryCost + federalTax + gasSupplyCharge
        totalCost *= 1.13 #HST
    elif(region == 2):
        totalCost = 23.98 #Customer base charge
        if (cubicmeters <= 100 ):
            deliveryCost = cubicmeters * 0.168647
        elif (cubicmeters <= 300):
            deliveryCost =100 * 0.168647 + (cubicmeters-100) * 0.165874 
        elif (cubicmeters <= 500):
            deliveryCost =100 * 0.168647 + 200 * 0.165874 + (cubicmeters-300) * 0.161477
        elif (cubicmeters <= 1000):
            deliveryCost = 100 * 0.168647 + 200 * 0.165874 + 200 * 0.161477 + (cubicmeters-500)*0.157444
        elif (cubicmeters > 1000):
            deliveryCost = 100 * 0.168647 + 200 * 0.165874 + 200 * 0.161477 + 500 * 0.157444 + (cubicmeters-1000) * 0.154108
        
        transportationCost = cubicmeters * 0.019418 #Transportation Charge
        costAdjustment = cubicmeters * 0.000484 #Cost Adjustment
        federalTax = cubicmeters * 0.1239 #Federal Carbon charge
        gasSupplyCharge = cubicmeters *  0.182917

        totalCost += deliveryCost + transportationCost + costAdjustment + federalTax + gasSupplyCharge
        totalCost *= 1.13 #HST

    elif(region == 3):
        totalCost = 23.98 #Customer base charge
        if (cubicmeters <= 100 ):
            deliveryCost = cubicmeters * 0.131894
        elif (cubicmeters <= 300):
            deliveryCost =100 * 0.0168647 + (cubicmeters-100) * 0.129121 
        elif (cubicmeters <= 500):
            deliveryCost =100 * 0.0168647 + 200 * 0.129121 + (cubicmeters-300) * 0.124724
        elif (cubicmeters <= 1000):
            deliveryCost =100 * 0.0168647 + 200 * 0.129121 + 200 * 0.124724+ (cubicmeters-500)* 0.120691 
        elif (cubicmeters > 1000):
            deliveryCost =100 * 0.0168647 + 200 * 0.129121 + 200 * 0.124724+500 * 0.120691 +  (cubicmeters-1000) * 0.117355

        transportationCost = cubicmeters * 0.033226 #Transportation Charge
        costAdjustment = cubicmeters * 0.004279 #Cost Adjustment
        federalTax = cubicmeters * 0.1239 #Federal Carbon charge
        gasSupplyCharge = cubicmeters * 0.114990
        
        totalCost += deliveryCost + transportationCost + costAdjustment + federalTax + gasSupplyCharge
        totalCost *= 1.13 #HST
    elif(region == 4):
        totalCost = 22.88
        if (cubicmeters <= 30 ):
            deliveryCost = cubicmeters * 0.121232
        elif (cubicmeters <= 85):
            deliveryCost = 30 * 0.121232 + (cubicmeters-30) * 0.114516
        elif (cubicmeters <= 170):
            deliveryCost = 30 * 0.121232 + 55 * 0.11451 + (cubicmeters-85) * 0.109256 
        elif (cubicmeters > 170):
            deliveryCost = 30 * 0.121232 + 55 * 0.11451 + 85 * 0.109256 + (cubicmeters-170) * 0.105336

        transportationCost = (cubicmeters * 0.047411) + (cubicmeters * 0.009239) #Transportation Charge
        costAdjustment = cubicmeters * 0.007284 #Cost Adjustment
        federalTax = cubicmeters * 0.1239 #Federal Carbon charge
        gasSupplyCharge = cubicmeters * 0.137883

        totalCost += deliveryCost + transportationCost + costAdjustment + federalTax
        totalCost *= 1.13 #HST

    return 0

def give_suggestions():
    print("Based on your information, we can now determine what options are available to you to lower your costs")
    income = float(input("What is your average yearly income: "))
    members = float(input("How many members live in your household: "))
    if(income < 20000):
        if(members == 1):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 45$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
        elif(members == 2):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 45$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
        elif(members == 3):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 51$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
        elif(members == 4):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 57$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
        elif(members == 5):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 63$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
        elif(members == 6):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 75$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
        elif(members == 7):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 75$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
    elif(income < 39000):
        if(members == 2):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 40$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
        elif(members == 3):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 45$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
        elif(members == 4):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 51$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
        elif(members == 5):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 57$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
        elif(members == 6):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 63$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
        elif(members == 7):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 75$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
    elif(income < 48000):
        if(members == 3):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 35$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
        elif(members == 4):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 40$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
        elif(members == 5):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 45$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
        elif(members == 6):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 51$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
        elif(members == 7):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 57$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
    elif(income < 52000):
        if(members == 5):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 35$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
        elif(members == 6):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 40$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
        elif(members == 7):
            print("With the Ontario Electricity Support program, you seem to be eligible to recieve 45$ per month to help with energy costs. If you use electric heating, you may be eligible to gain increased support from 52$ to 113$ ")
    else:
        print("It doesnt seem like you are eligible for the Ontario Electricity Support program at the moment")
    
    print("Installing Low-E coating on windows can help trap solar heat in the home, reducing the burden on artificial heating means.\nEnergy loss is reduced up to 50 percent and lasts from 10 to 15 years ")
    print("Sealing windows with Silicon sealant improves energy efficiency and preventing heat loss.")
    
get_user_information()


#DISCLAIMER
#This program does not take into account number of household members when calculating BTU needed