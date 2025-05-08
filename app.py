# imported libraries
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np
import pickle
import os
import hashlib
from datetime import datetime

#page config
st.set_page_config(page_title="RFM Analysis Dashboard", page_icon="📊", layout="wide")

#display logo
def display_logo():
    cols = st.columns([1, 3])
    with cols[0]:
        st.image("/Users/desiree/Desktop/Screen Shot 2025-03-03 at 7.44.49 PM.png", width=150)

#store user 
def initialize_users():
    if not os.path.exists("users.pkl"):
        with open("users.pkl", "wb") as f:
            pickle.dump({}, f)

#hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

#save users
def save_users(users):
    with open("users.pkl", "wb") as f:
        pickle.dump(users, f)

#load users
def load_users():
    try:
        with open("users.pkl", "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError):
        return {}

#register user
def register_user(username, password, email):
    users = load_users()
    
    #check if username already exists
    if username in users:
        return False, "Username already exists. Please choose another."
    
    #create new user 
    users[username] = {
        "password": hash_password(password),
        "email": email,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_login": None
    }
    
    save_users(users)
    return True, "Registration successful! You can now login."

#authenticate user
def authenticate(username, password):
    users = load_users()
    
    if username not in users:
        return False, "Username not found."
    
    stored_password = users[username]["password"]
    if stored_password == hash_password(password):
        
        users[username]["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_users(users)
        return True, "Login successful!"
    else:
        return False, "Incorrect password."

#load data
@st.cache_data 
def load_data():
    df = pd.read_csv('supermarket_sales.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    return df

#login page
def auth_page():
    #display logo 
    st.image("/Users/desiree/Desktop/Screen Shot 2025-03-03 at 7.44.49 PM.png", width=200)
    
    st.title("RFM Analysis Dashboard")
    
    #CSS
    st.markdown("""
    <style>
    .auth-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f8f9fa;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .auth-header {
        text-align: center;
        color: #1E88E5;
        margin-bottom: 20px;
    }
    .tab-content {
        padding: 20px 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    
    #login and registration tabs
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
        st.markdown("<h2 class='auth-header'>Login</h2>", unsafe_allow_html=True)
        
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            login_button = st.button("Login")
        
        if login_button:
            if not login_username or not login_password:
                st.error("Please enter both username and password")
            else:
                success, message = authenticate(login_username, login_password)
                if success:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = login_username
                    st.success(message)
                    
                    st.rerun()
                else:
                    st.error(message)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab2:
        st.markdown("<div class='tab-content'>", unsafe_allow_html=True)
        st.markdown("<h2 class='auth-header'>Register</h2>", unsafe_allow_html=True)
        
        reg_user = st.text_input("Username", key="reg_username")
        reg_email = st.text_input("Email", key="reg_email")
        reg_pass = st.text_input("Password", type="password", key="reg_password")
        reg_confirm_pass = st.text_input("Confirm Password", type="password", key="reg_confirm_password")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            register_button = st.button("Register")
        
        if register_button:
            if not reg_user or not reg_email or not reg_pass:
                st.error("Please fill in all fields")
            elif reg_pass != reg_confirm_pass:
                st.error("Passwords do not match")
            elif len(reg_pass) < 6:
                st.error("Password must be at least 6 characters long")
            else:
                success, message = register_user(reg_user, reg_pass, reg_email)
                if success:
                    st.success(message)
                else:
                    st.error(message)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def main():
    #display logo 
    display_logo()
    
    #logout button on sidebar
    if st.session_state.get("authenticated", False):
        st.sidebar.title(f"Welcome, {st.session_state['username']}!")
        if st.sidebar.button("Logout"):
            st.session_state["authenticated"] = False
            st.session_state["username"] = None
            st.rerun()
    
    #upload file 
    uploaded_file = st.sidebar.file_uploader("Upload your customer data CSV", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            df['Date'] = pd.to_datetime(df['Date'])
            st.sidebar.success("Upload Successful")
        except Exception as e:
            st.sidebar.error(f"Error uploading file: {e}")
            df = load_data()
    else:
        try:
            df = load_data()
        except Exception as e:
            st.error(f"Error loading data: {e}")
            st.error("Please make sure 'supermarket_sales.csv' exists in the current directory.")
            st.stop()

    #title and description
    st.title("📊 RFM Analysis Dashboard")
    st.markdown("""
    This dashboard analyzes customer behavior using RFM (Recency, Frequency, Monetary) metrics:
    * **Recency**: Days since last purchase
    * **Frequency**: Number of purchases
    * **Monetary**: Total spending
    """)

    #sidebar filter for date and transaction
    st.sidebar.header("Filters")

    #date range
    try:
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(df['Date'].min().date(), df['Date'].max().date()),
            min_value=df['Date'].min().date(),
            max_value=df['Date'].max().date(),
            key='date_range_filter'
        )
    except Exception as e:
        st.sidebar.error(f"Error with date input: {e}")
        st.stop()

    #slider
    try:
        transaction_amount = st.sidebar.slider(
            "Transaction Amount Range",
            min_value=float(df['Total'].min()),
            max_value=float(df['Total'].max()),
            value=(float(df['Total'].min()), float(df['Total'].max())),
            key='transaction_amount_slider'
        )
    except Exception as e:
        st.sidebar.error(f"Error with slider: {e}")
        st.stop()

    #data filter
    filtered_df = df[
        (df['Date'] >= pd.to_datetime(date_range[0])) & 
        (df['Date'] <= pd.to_datetime(date_range[1])) &
        (df['Total'].between(transaction_amount[0], transaction_amount[1]))
    ]

    if filtered_df.empty:
        st.warning("No data matches the current filters. Please adjust your selection.")
        st.stop()

    #RFM Calculation
    current_date = filtered_df['Date'].max()

    invoice_ids = filtered_df['Invoice ID'].unique()

    #lists to store results
    recency_values = []
    frequency_values = []
    monetary_values = []
    invoice_id_list = []

    #calculate RFM
    for invoice_id in invoice_ids:
        invoice_data = filtered_df[filtered_df['Invoice ID'] == invoice_id]
        
        #recency
        latest_date = invoice_data['Date'].max()
        recency = (current_date - latest_date).days
        
        #frequency 
        frequency = len(invoice_data)
        
        #monetary 
        monetary = invoice_data['Total'].sum()
        
        #append
        invoice_id_list.append(invoice_id)
        recency_values.append(recency)
        frequency_values.append(frequency)
        monetary_values.append(monetary)

    #RFM DataFrame
    rfm_data = {
        'Invoice ID': invoice_id_list,
        'Recency': recency_values,
        'Frequency': frequency_values,
        'Monetary': monetary_values
    }
    rfm = pd.DataFrame(rfm_data)

    #bins 
    recency_bins = [0, 30, 90, 180, 365]  
    frequency_bins = [1, 2, 5, 10, 20]    
    monetary_bins = [0, 500, 1000, 5000, 10000]  

    #labels
    recency_labels = ['1', '2', '3', '4']
    frequency_labels = ['4', '3', '2', '1']
    monetary_labels = ['4', '3', '2', '1']

    #segmenting with pd.cut
    try:
        rfm['R'] = pd.cut(rfm['Recency'], bins=recency_bins, labels=recency_labels, include_lowest=True)
        rfm['F'] = pd.cut(rfm['Frequency'], bins=frequency_bins, labels=frequency_labels, include_lowest=True)
        rfm['M'] = pd.cut(rfm['Monetary'], bins=monetary_bins, labels=monetary_labels, include_lowest=True)
        
        #convert to string 
        rfm['R'] = rfm['R'].astype(str)
        rfm['F'] = rfm['F'].astype(str)
        rfm['M'] = rfm['M'].astype(str)
        
        rfm['R'] = rfm['R'].replace('nan', 'Other')
        rfm['F'] = rfm['F'].replace('nan', 'Other')
        rfm['M'] = rfm['M'].replace('nan', 'Other')
    except Exception as e:
        st.error(f"Error creating RFM segments: {e}")

    #RFM combined score
    rfm['RFM_Score'] = rfm['R'] + rfm['F'] + rfm['M']
    
    #customer segment based on RFM score
    def assign_segment(row):
        score = row['RFM_Score']
        r_score = int(row['R']) if row['R'] != 'Other' else 0
        f_score = int(row['F']) if row['F'] != 'Other' else 0
        m_score = int(row['M']) if row['M'] != 'Other' else 0
        
        #Loyal Customers
        if r_score >= 2 and f_score >= 3 and m_score >= 3:
            return 'Loyal Customers'
        #At Risk
        elif r_score <= 2 and f_score >= 2:
            return 'At Risk'
        #New Customers 
        elif frequency_values[invoice_id_list.index(row['Invoice ID'])] <= 2:
            return 'New Customers'
        else:
            return 'Others'
    
    #apply segment function
    rfm['Segment'] = rfm.apply(assign_segment, axis=1)

    #dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Data Explorer", "Customer Segments", "About"])
    
    with tab1:
        #calculate and display metrics
        total_customers = len(rfm)
        average_recency = np.mean(rfm['Recency'])
        average_frequency = np.mean(rfm['Frequency'])
        average_monetary = np.mean(rfm['Monetary'])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Customers", total_customers)
        col2.metric("Average Recency", f"{average_recency:.2f} days")
        col3.metric("Average Frequency", f"{average_frequency:.2f} purchases")
        col4.metric("Average Monetary", f"${average_monetary:.2f}")

        #pie chart
        try:
            st.subheader("Customer Segment Distribution")
            segment_counts = rfm['Segment'].value_counts().reset_index()
            segment_counts.columns = ['Segment', 'Count']
            
            fig_segment = px.pie(
                segment_counts, 
                values='Count', 
                names='Segment', 
                title='Customer Segments Distribution',
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            st.plotly_chart(fig_segment, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating segment pie chart: {e}")
#new visualizations
        st.header("RFM Score Analysis")
        
        #individual RFM scores
        try:
            r_col, f_col, m_col = st.columns(3)
            
            with r_col:
                r_counts = rfm['R'].value_counts().reset_index()
                r_counts.columns = ['R_Score', 'Count']
                
                fig_r = px.pie(
                    r_counts,
                    values='Count',
                    names='R_Score',
                    title='Recency Score Distribution',
                    hole=0.4
                )
                fig_r.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_r, use_container_width=True)
            
            with f_col:
                f_counts = rfm['F'].value_counts().reset_index()
                f_counts.columns = ['F_Score', 'Count']
                
                fig_f = px.pie(
                    f_counts,
                    values='Count',
                    names='F_Score',
                    title='Frequency Score Distribution',
                    hole=0.4
                )
                fig_f.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_f, use_container_width=True)
            
            with m_col:
                m_counts = rfm['M'].value_counts().reset_index()
                m_counts.columns = ['M_Score', 'Count']
                
                fig_m = px.pie(
                    m_counts,
                    values='Count',
                    names='M_Score',
                    title='Monetary Score Distribution',
                    hole=0.4
                )
                fig_m.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_m, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating individual RFM score charts: {e}")
        
        #score Distribution Pie Chart
        try:
            st.subheader("RFM Score Distribution")
            
            score_counts = rfm['RFM_Score'].value_counts()
            top_scores = score_counts.nlargest(7).index.tolist()
            
            rfm['Score_Group'] = rfm['RFM_Score'].apply(lambda x: x if x in top_scores else 'Other Scores')
            
            score_group_counts = rfm['Score_Group'].value_counts().reset_index()
            score_group_counts.columns = ['RFM_Score', 'Count']
            
            #create pie chart
            fig_score_pie = px.pie(
                score_group_counts,
                values='Count',
                names='RFM_Score',
                title='Distribution of RFM Scores',
                color_discrete_sequence=px.colors.qualitative.Pastel1
            )
            fig_score_pie.update_traces(textposition='inside', textinfo='percent+label')
            
            st.plotly_chart(fig_score_pie, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating RFM score distribution chart: {e}")

        #3D visualization
        try:
            st.subheader("3D RFM Visualization")
            # sample data 
            if len(rfm) > 1000:
                sample_rfm = rfm.sample(1000, random_state=42)
                fig_3d = px.scatter_3d(
                    sample_rfm, x='Recency', y='Frequency', z='Monetary', 
                    color='Segment',
                    title="3D Visualization of RFM Metrics (1000 sample points)"
                )
            else:
                fig_3d = px.scatter_3d(
                    rfm, x='Recency', y='Frequency', z='Monetary', 
                    color='Segment',
                    title="3D Visualization of RFM Metrics"
                )
            st.plotly_chart(fig_3d, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating 3D scatter plot: {e}")
    
    with tab2:
        st.subheader("RFM Data Explorer")
        
        #search and filter options
        search_col, filter_col = st.columns(2)
        
        with search_col:
            search_term = st.text_input("Search by Invoice ID", "")
        
        with filter_col:
            segment_filter = st.multiselect(
                "Filter by Segment",
                options=['All'] + list(rfm['Segment'].unique()),
                default=['All']
            )
        
        #apply filters
        filtered_rfm = rfm.copy()
        
        if search_term:
            filtered_rfm = filtered_rfm[filtered_rfm['Invoice ID'].str.contains(search_term, case=False)]
        
        if segment_filter and 'All' not in segment_filter:
            filtered_rfm = filtered_rfm[filtered_rfm['Segment'].isin(segment_filter)]
        
        #data table
        st.markdown("### RFM Data")
        rfm_html = filtered_rfm.head(50).to_html(index=False)
        st.markdown(rfm_html, unsafe_allow_html=True)
        
        st.subheader("Export Data")
        try:
            csv_data = filtered_rfm.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download Filtered RFM Data",
                csv_data,
                "rfm_filtered_data.csv",
                "text/csv",
                key='download_csv_button'
            )
        except Exception as e:
            st.error(f"Error creating download button: {e}")
    
    with tab3:
        st.subheader("Customer Segmentation Analysis")
        
        #segment descriptions
        segment_descriptions = {
            "Loyal Customers": "Consistent and dependable customers",
            "New Customers": "Customers who purchased recently but not made many purchases as yet",
            "At Risk": "Customers who haven't purchased recently",
        }
        
        #segment metrics
        segment_metrics = rfm.groupby('Segment').agg({
            'Recency': 'mean',
            'Frequency': 'mean',
            'Monetary': 'mean',
            'Invoice ID': 'count'
        }).reset_index()
        
        segment_metrics = segment_metrics.rename(columns={
            'Invoice ID': 'Count',
            'Recency': 'Avg Days Since Purchase',
            'Frequency': 'Avg Purchase Frequency',
            'Monetary': 'Avg Spend ($)'
        })
        
        segment_metrics['Avg Days Since Purchase'] = segment_metrics['Avg Days Since Purchase'].round(1)
        segment_metrics['Avg Purchase Frequency'] = segment_metrics['Avg Purchase Frequency'].round(1)
        segment_metrics['Avg Spend ($)'] = segment_metrics['Avg Spend ($)'].round(2)
        
        #add New Customers
        segment_options = segment_metrics['Segment'].tolist()
        if 'New Customers' not in segment_options:
            segment_options.append('New Customers')
            
        selected_segment = st.selectbox(
            "Select Customer Segment to Analyze",
            options=segment_options
        )
        
       
        if selected_segment == 'New Customers' and 'New Customers' not in segment_metrics['Segment'].values:
            new_customers = rfm[rfm['Frequency'] <= 2]
            
            #metrics for New Customers
            new_customers_count = len(new_customers)
            avg_recency = np.mean(new_customers['Recency']) if len(new_customers) > 0 else 0
            avg_frequency = np.mean(new_customers['Frequency']) if len(new_customers) > 0 else 0
            avg_monetary = np.mean(new_customers['Monetary']) if len(new_customers) > 0 else 0
            
            st.markdown(f"### {selected_segment}")
            st.markdown(f"**Description**: {segment_descriptions.get(selected_segment, 'Customers who purchased recently but not made many purchases as yet')}")
        else:
            
            segment_data = segment_metrics[segment_metrics['Segment'] == selected_segment].iloc[0]
            
            st.markdown(f"### {selected_segment}")
            st.markdown(f"**Description**: {segment_descriptions.get(selected_segment, 'No description available')}")
        
        #metrics for the selected segment
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        if selected_segment == 'New Customers' and 'New Customers' not in segment_metrics['Segment'].values:
            #metrics for new customers
            with metric_col1:
                st.metric("Number of Customers", new_customers_count)
            
            with metric_col2:
                st.metric("Avg Days Since Purchase", f"{avg_recency:.2f} days")
            
            with metric_col3:
                st.metric("Avg Purchase Frequency", f"{avg_frequency:.2f}")
            
            with metric_col4:
                st.metric("Avg Spend ($)", f"${avg_monetary:.2f}")
        else:
            # Show regular segment metrics
            with metric_col1:
                st.metric("Number of Customers", int(segment_data['Count']))
            
            with metric_col2:
                st.metric("Avg Days Since Purchase", segment_data['Avg Days Since Purchase'])
            
            with metric_col3:
                st.metric("Avg Purchase Frequency", segment_data['Avg Purchase Frequency'])
            
            with metric_col4:
                st.metric("Avg Spend ($)", f"${segment_data['Avg Spend ($)']}")
        
        #RFM Distribution for segment
        try:
            if selected_segment == 'New Customers' and 'New Customers' not in segment_metrics['Segment'].values:
                #distribution for new customers
                if len(new_customers) > 0:
                    fig_box = go.Figure()
                    fig_box.add_trace(go.Box(y=new_customers['Recency'], name="Recency"))
                    fig_box.add_trace(go.Box(y=new_customers['Frequency'], name="Frequency"))
                    fig_box.add_trace(go.Box(y=new_customers['Monetary'], name="Monetary"))
                    fig_box.update_layout(title=f"Distribution of RFM Metrics for {selected_segment}")
                    st.plotly_chart(fig_box, use_container_width=True)
                else:
                    st.warning("No new customers found in the current data selection.")
            else:
                segment_rfm = rfm[rfm['Segment'] == selected_segment]
                
                fig_box = go.Figure()
                fig_box.add_trace(go.Box(y=segment_rfm['Recency'], name="Recency"))
                fig_box.add_trace(go.Box(y=segment_rfm['Frequency'], name="Frequency"))
                fig_box.add_trace(go.Box(y=segment_rfm['Monetary'], name="Monetary"))
                fig_box.update_layout(title=f"Distribution of RFM Metrics for {selected_segment}")
                st.plotly_chart(fig_box, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating box plot: {e}")
        
        #marketing recommendations based on segment
        st.subheader("Marketing Recommendations")
        
        recommendations = {
           
            "Loyal Customers": [
                "Give early access to sales",
                "Exclusive discounts and other personalized experiences to shopw appreciation",
                "Upgrade them to a card with higher limit",
                "Consider brand deal (depending on influence)"
            ],
            "New Customers": [
                 "Encourage credit card application",
                "Offer a coupon for free shipping with first online purchase",
                "Encourage application download by explaining rewards program potential",
                "Register them for emails"
            ],
            "At Risk": [
                "Send surveys to identify qualms",
                "Incentivize them to come back with exclusive promotions",
                "Send promotional emails on your products making them more desirable",
                "Follow up on most recent purchases to inquire about product satisfaction"
            ],
            
        }
        
        segment_recommendations = recommendations.get(selected_segment, ["No specific recommendations available for this segment"])
        
        for i, rec in enumerate(segment_recommendations, 1):
            st.markdown(f"**{i}. {rec}**")
            
        #data table and export for New Customers
        if selected_segment == 'New Customers' and 'New Customers' not in segment_metrics['Segment'].values:
            st.subheader("New Customer Data")
            
            if len(new_customers) > 0:
                #display first 50 rows as HTML
                rfm_html = new_customers.head(50).to_html(index=False)
                st.markdown(rfm_html, unsafe_allow_html=True)
                
                st.subheader("Export Data")
                try:
                    csv_data = new_customers.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Download New Customer Data",
                        csv_data,
                        "new_customers_data.csv",
                        "text/csv",
                        key='download_new_customer_button'
                    )
                except Exception as e:
                    st.error(f"Error creating download button: {e}")
            else:
                st.info("No new customer data available to display.")

    #about Tab
    with tab4:
        st.title("About RFM Analysis")
        st.markdown("""
        This section provides information about RFM analysis, its benefits, and how to use this dashboard.
        """)
        
        #create dropdowns
        with st.expander("What is RFM Analysis?"):
             st.markdown("""
            The RFM Analysis System categorizes customers based on: Recency (R): How recently a customer made a purchase. Frequency (F): How often a customer makes purchases. Monetary Value (M): How much a customer spends. Traditional segmentation approaches, such as demographic and geographic segmentation, fail to capture the complexities of customer behavior. Demographic data is the data that segments customers based on the attributes like age, gender, income, etc. Attributes like these are useful for identifying the border, more general trends. The geographical segmentation in-of-itself is even more simple, focusing on location-specific patterns but disregarding the nuances of the singular customer. Marketing for customers in a complex and intricate system, and solely focusing on demographic/geographical segmentation could, and often does, result in ineffective marketing techniques.
            """)

        with st.expander("Benefits of RFM Segmentation"):
            st.markdown("""
            An RFM (Recency, Frequency, Monetary) analysis system solves this by segmenting customers based on recency (the customers purchasing habits), frequency (specifically how recently they've made a purchase), and monetary (how often they buy, and how much they spend). This approach allows businesses to identify high-value customers, those at risk of churning, and occasional buyers who could be encouraged to spend more allowing a company to directly refine marketing strategies. This RFM system will allow us to provide an accessible and user-friendly tool that automates customer segmentation which in turn can help businesses focus on valuable customers, save time on manual data analysis, and create personalized marketing strategies. Unlike traditional methods, our system is designed to be accessible, requiring minimal technical expertise, so that companies of all sizes can benefit from behavior-based customer insights.
            """)

        with st.expander("How to Interpret RFM Scores"):
            st.markdown("""
            By automating the RFM analysis process, businesses can quickly identify customer groups, including VIPs, at-risk customers, and dormant buyers. Since some companies don't have the resources or knowledge on how to manually perform RFM analysis, our system will address this need by streamlining RFM scoring and making the insights easier to understand through the use of visual dashboards. It must properly calculate RFM data with high accuracy and normalize and categorize scores into customer segments accurately and efficiently. This allows store owners to identify which products have better customer retention so they can pour more into that area and hopefully see more profit in return. Regional managers can compare the categorizations of customer segments across all stores to then see which tactics are proving to be most successful and implement them across other locations.
            This system interprets RFM scores on a 1-4 scale:
            - Recency (1-4): 4 = very recent purchase, 1 = purchase long ago
            - Frequency (1-4): 4 = frequent purchaser, 1 = one-time buyer
            - Monetary (1-4): 4 = high spender, 1 = low spender
    
            Customer segment rfm scores:
            - Loyal (R:4, F:4, M:4): Best customers who purchase recently, frequently, and spend the most
            - At Risk (R:1, F:3-4, M:3-4): Previously valuable customers who haven't purchased recently
            - New Customers (R:4, F:1, M:1-4): First-time buyers
            
            """)

        with st.expander("How This Application Drives Business Success"):
            st.markdown(""" Our system allows us to address the gaps in traditional segmentation methods using practicality and transformivity. We come across the issue posed by the approaches that are more one-size-fits all and outdated in order to understand the dynamics of the customer base. This system leverages behavior-based metrics and scalable technology, in turn enabling businesses to optimize customer segmentation, improve retention strategies, and drive informed decision-making. This system automates what used to be an overly-complex process, saves time, and ensures accuracy and scalability in order to create the flexibility and potential needed to adapt to real-world business needs. By adopting the RFM analysis system, businesses will have an opportunity to gain both a useful tool, and something more that's crucial to success. Graining precisions, clarity and an understanding of how to make 'smarter' decisions in order for businesses to create a meaningful, lasting relationship with their customers all through the improvement of customer segmentation.
            """)
            
        with st.expander("How to Format Your Customer Data for Upload"):
            st.markdown("""
            ### Customer Data Format Requirements
            
            To successfully upload your own customer data to this dashboard, please ensure your CSV file follows these format requirements:
            
            #### Required Columns:
            - **Invoice ID**: A unique identifier for each transaction (text or numeric)
            - **Date**: Transaction date in a standard format (YYYY-MM-DD)
            - **Total**: Transaction amount (numeric value)
            
            #### Example Data Format:
            | Invoice ID | Date | Total | Other Columns (Optional) |
            |------------|------|-------|--------------------------|
            | INV-001 | 2023-01-15 | 125.50 | ... |
            | INV-002 | 2023-01-16 | 85.75 | ... |
            | INV-003 | 2023-01-20 | 210.25 | ... |
            
            #### Important Notes:
            - Make sure your date format is consistent
            - Transaction amounts should be numeric (no currency symbols in the data)
            - The system identifies unique customers by Invoice ID
            - Additional columns in your CSV will be preserved but not used in the RFM calculation
            - For best results, include at least 3 months of transaction data
            
            You can download a sample template below to help format your data correctly.
            """)
            
#initialize users database
initialize_users()

#initialize session state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

#check if user is authenticated
if st.session_state["authenticated"]:
    main()
else:
    auth_page()
