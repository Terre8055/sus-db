# Data Persistency Design and Architecture

Data architecture where we have a single store or repository, that we call a central station using redis which synchronises with individual stores, which we call IRs. Now every client or user when signs up is allocated a store or repo which uses the native python dbm. And when the individual dbm by python is updated, it puts a snapshot to the central store, which in turns syncs and updates the remaining IRs.

Since we hate an SPOF, we also have CS slaves which also go in sync with the CS. 

**Model Schema for User**

- user_string: `Secure User String eg. <g26454xd87q5>` //to be hashed and transformed into a `user_name` after serialization for ux.
- user_name: `default=None` 
**Example Flow:**

1. User signs up and provides a Secure User String (e.g., "").
2. The provided user_string is hashed and transformed to create a user_name (e.g., "user123").
3. The user_name ("user123") is associated with the user's account, providing a username for the user.
4. The original Secure User String is securely hashed and stored in the user's data store for authentication and identification purposes.

![sus_db_design](images/diagram_sus.png)
