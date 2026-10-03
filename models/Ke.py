from models.globals import results

# ============================================================
# COST OF EQUITY
# ============================================================

def calculate_ke(rf,erp,beta):
    
    global results

    ke = rf + beta * erp

    print(f"The ke is : {ke}")

    results["ke"]=ke

    return ke