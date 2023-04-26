# Welcome to the MindsDB Manual QA Testing for Snowflake Handler

> **Please submit your PR in the following format after the underline below `Results` section. Don't forget to add an underline after adding your changes i.e., at the end of your `Results` section.**

## Testing Snowflake Handler with [Dataset Name](URL to the Dataset)

**1. Testing CREATE DATABASE**

CREATE DATABASE test  
WITH ENGINE = 'snowflake',    
PARAMETERS = {
  "user": "mprathyusha",                --- Your database user.
  "account": "TL57441 ",             --- Snowflake account.
  "warehouse": "COMPUTE_WH",           --- warehouse account.
  "protocol": "https",            --- Common https
  "schema": "PUBLIC",              --- common schema PUBLIC.
  "password": "Prathyu@7175",            --- Your password.
  "host": "sbyyyzr-tl57441.snowflakecomputing.com",                --- host, it can be an ip or an url.
  "port": "443",              --- common port is 443.
  "database": "test"             --- The name of your database *optional.
};
![CREATE_DATABASE](Image URL of the screenshot)
![image](https://user-images.githubusercontent.com/62796352/231744745-afddc0f7-b1d2-4292-be75-589ee491d48c.png)




**2. Testing CREATE PREDICTOR**


CREATE MODEL test_model
FROM test (
  SELECT * FROM test_table2
  )
PREDICT TARGETT;


![CREATE_PREDICTOR](Image URL of the screenshot)
![image](https://user-images.githubusercontent.com/62796352/231745156-d18368cb-d2f1-40f8-ba9c-9c977b51285d.png)



**3. Testing SELECT FROM PREDICTOR**


SELECT *
FROM mindsdb.models 
where name = 'test_model';

![SELECT_FROM](Image URL of the screenshot)
![image](https://user-images.githubusercontent.com/62796352/231745424-ee7457d3-f191-4d8e-807c-432c9d65eaa2.png)


**4. Testing DROP THE DATABASE**

DROP DATABASE test;

![DROP_DB](Image URL of the screenshot)
![image](https://user-images.githubusercontent.com/62796352/231745696-37dfbd24-827c-4566-93f4-b19c0de0d721.png)




### Results

Drop a remark based on your observation.
- [x] Works Great 💚 (This means that all the steps were executed successfuly and the expected outputs were returned.)
- [ ] There's a Bug 🪲 [Issue Title](URL To the Issue you created) ( This means you encountered a Bug. Please open an issue with all the relevant details with the Bug Issue Template)

---
