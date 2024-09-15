# app/main.py

import logging
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from app.db import get_db_connection
from app.auth import authenticate_user, create_access_token, get_current_active_user, User, fake_users_db, ACCESS_TOKEN_EXPIRE_MINUTES

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


app = FastAPI()


# Endpoint to generate a token
@app.post("/token", response_model=dict)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Endpoint to fetch collection data
@app.get("/api/v1/pos/fetch-collection")
async def fetch_collection_data(current_user: User = Depends(get_current_active_user)):
    collect_itemcodes = ['0000000001']
    collect_code_list = ', '.join(['%s'] * len(collect_itemcodes))  # Correct number of placeholders

    logger.debug("Preparing SQL query for fetch-collection")

    # SQL query with dynamically created placeholders
    collection_query = f"""
    SELECT 
        tor.GuestChkNo as guestcheck,
        tori.OrderID as orderid,
        SUM(tori.PriceShow) AS amount,
        SUBSTRING(MAX(CASE 
                WHEN tori.ItemCode IN ({collect_code_list})
                THEN tori.ItemName 
            END), 4, LEN(MAX(CASE 
                WHEN tori.ItemCode IN ({collect_code_list})
                THEN tori.ItemName 
            END))) AS member_ref,
        MAX(CASE 
                WHEN tori.ItemCode IN ({collect_code_list})
                THEN tori.CreateDate 
            END) AS createddate,
        'COLLECT' as mtype
    FROM 
        tOrderItem tori
    JOIN tOrder tor
    ON tori.OrderID=tor.OrderID
    GROUP BY 
        tor.GuestChkNo,
        tori.OrderID
    HAVING 
        COUNT(CASE WHEN tori.ItemCode IN ({collect_code_list}) THEN 1 END) > 0;
    """

    # logger.debug(f"SQL query prepared: {collection_query}")
    # logger.debug(f"Collect item codes: {collect_itemcodes}")

    try:
        logger.debug("Connecting to SQL Server")
        conn = get_db_connection()
        cursor = conn.cursor()
        logger.debug("Executing SQL query")
        
        # Repeat the collect_itemcodes for each placeholder used in the query
        parameters = collect_itemcodes * 4  # Repeat parameters to match the IN clause placeholders count
        cursor.execute(collection_query, parameters)

        results = cursor.fetchall()
        logger.debug(f"Query executed successfully, fetched {len(results)} rows")
        
        cursor.close()
        conn.close()
        logger.debug("SQL Server connection closed")

        # Return the results
        return [{"guestcheck": row[0], "orderid": row[1], "amount": row[2],
                 "member_ref": row[3], "createddate": row[4], "mtype": row[5]} for row in results]

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    

# Endpoint to fetch redemption data
@app.get("/api/v1/pos/fetch-redemption")
async def fetch_redemption_data(current_user: User = Depends(get_current_active_user)):
    redeem_typecode = ['999']
    redeem_typecode_list = ', '.join(['%s'] * len(redeem_typecode))

    logger.debug("Preparing SQL query for fetch-redemption")

    # SQL query with placeholders
    redemption_query = f"""
    SELECT 
        tor.GuestChkNo as guestcheck,
        topy.OrderID as orderid, 
        topy.Amount as amount, 
        topy.Extinfo1 as member_ref,
        topy.CreateDate as createddate,
        'REDEEM' as mtype
    FROM tOrderPayment topy
    JOIN tOrder tor
    ON topy.OrderID=tor.OrderID
    WHERE Pycode IN ({redeem_typecode_list});
    """
    # logger.debug(f"SQL query prepared: {redemption_query}")
    # logger.debug(f"Redeem type codes: {redeem_typecode}")

    try:
        # Fetch data from SQL Server
        logger.debug("Connecting to SQL Server")
        conn = get_db_connection()
        cursor = conn.cursor()
        logger.debug("Executing SQL query")
        cursor.execute(redemption_query, redeem_typecode)
        results = cursor.fetchall()
        logger.debug(f"Query executed successfully, fetched {len(results)} rows")
        
        cursor.close()
        conn.close()
        logger.debug("SQL Server connection closed")

        # Return the results
        return [{"guestcheck": row[0], "orderid": row[1], "amount": row[2],
                 "member_ref": row[3], "createddate": row[4], "mtype": row[5]} for row in results]

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")