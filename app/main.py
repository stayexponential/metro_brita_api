# app/main.py

import logging
from fastapi import FastAPI, HTTPException
from app.db import get_db_connection

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


app = FastAPI()

# Endpoint to fetch collection data
@app.get("/fetch-collection")
async def fetch_collection_data():
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

    logger.debug(f"SQL query prepared: {collection_query}")
    logger.debug(f"Collect item codes: {collect_itemcodes}")

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
@app.get("/fetch-redemption")
async def fetch_redemption_data():
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
    logger.debug(f"SQL query prepared: {redemption_query}")
    logger.debug(f"Redeem type codes: {redeem_typecode}")

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