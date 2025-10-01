#!/usr/bin/env python3
"""
ML Service for E-commerce Analytics
This service provides ML endpoints for churn prediction, customer segmentation, and sales forecasting.
"""

import sys
import os
import pandas as pd
import numpy as np
import json
from pathlib import Path

# Add the ecommerce_analytics_app to the Python path
current_dir = Path(__file__).parent
ecommerce_app_dir = current_dir.parent.parent / "ecommerce_analytics_app"
sys.path.append(str(ecommerce_app_dir))

try:
    from src.churn import churn_pipeline
    from src.segmentation import customer_segmentation
    from src.sales_forecast import sales_forecast_pipeline
except ImportError as e:
    print(f"Warning: Could not import ML modules: {e}")
    # Create mock functions for development
    def churn_pipeline(df):
        # Mock churn pipeline
        top_churners = df.head(10).copy()
        top_churners['churn_probability'] = np.random.uniform(0.1, 0.9, 10)
        metrics = {'average_churn_prob': 0.3, 'total_churners': 150}
        return top_churners, None, metrics, df
    
    def customer_segmentation(df):
        # Mock segmentation
        df['cluster'] = np.random.randint(0, 4, len(df))
        cluster_metrics = pd.DataFrame({
            'cluster': [0, 1, 2, 3],
            'count': [25, 30, 20, 25],
            'avg_recency': [30, 60, 90, 120]
        })
        return df, None, None, cluster_metrics
    
    def sales_forecast_pipeline(df):
        # Mock sales forecast
        top10_products = pd.DataFrame({
            'product_id': [f'P{i}' for i in range(1, 11)],
            'forecasted_sales': np.random.uniform(1000, 5000, 10)
        })
        demand_quarter = pd.DataFrame({
            'product_id': [f'P{i}' for i in range(1, 6)],
            'forecasted_sales': np.random.uniform(500, 2000, 5)
        })
        return {
            'top10_products': top10_products,
            'demand_quarter': demand_quarter,
            'mae': 0.15
        }

class MLService:
    def __init__(self):
        self.base_url = "http://localhost:5000"  # Flask app URL
    
    def analyze_file(self, file_path: str):
        """Analyze uploaded file and return basic info"""
        try:
            if file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)
            
            return {
                "success": True,
                "data": {
                    "rows": df.shape[0],
                    "columns": df.shape[1],
                    "filename": os.path.basename(file_path),
                    "description": df.describe().round(2).to_dict(),
                    "first5_records": df.head().to_dict(orient="records")
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def predict_churn(self, file_path: str):
        """Run churn prediction on uploaded file"""
        try:
            if file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)
            
            # Run churn pipeline
            top_churners, model, metrics, df_churn = churn_pipeline(df)
            
            # Add risk categories
            df_churn = self._categorize_churn_risk(df_churn)
            
            # Compute churn rate trends
            trends = self._churn_rate_trends(df_churn)
            
            # JSON-safe top 10
            top_churners_safe = top_churners.astype({'churn_probability': float}).to_dict(orient="records")
            
            # Customer churn risk groups count
            risk_groups = df_churn.groupby('churn_risk')['customer_id'].nunique().to_dict()
            
            return {
                "success": True,
                "data": {
                    "message": "Churn prediction completed!",
                    "average_churn_probability": float(metrics['average_churn_prob']),
                    "total_predicted_churners": int(metrics['total_churners']),
                    "top_10_customers_at_risk": top_churners_safe,
                    "customer_churn_risk_groups": risk_groups,
                    "churn_rate_trends": trends.to_dict(orient="records")
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def segment_customers(self, file_path: str):
        """Run customer segmentation on uploaded file"""
        try:
            if file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)
            
            # Aggregate features
            agg_dict = {
                'Recency': ('last_purchase_date', lambda x: (pd.Timestamp.today() - pd.to_datetime(x, errors='coerce').max()).days),
                'Frequency': ('order_id', 'count'),
                'Monetary': ('unit_price', lambda x: np.sum(pd.to_numeric(x, errors='coerce'))),
                'Avg_Rating': ('Ratings', 'mean'),
                'Tenure_Days': ('signup_date', lambda x: (pd.Timestamp.today() - pd.to_datetime(x, errors='coerce').min()).days)
            }
            if 'churn_prob' in df.columns:
                agg_dict['churn_prob'] = ('churn_prob', 'mean')
            
            df_agg = df.groupby('customer_id').agg(**agg_dict).reset_index()
            df_segmented, gmm, scaler, cluster_metrics = customer_segmentation(df_agg)
            
            # JSON-safe conversion
            df_segmented_safe = df_segmented.astype(object).where(pd.notnull(df_segmented), None).to_dict(orient="records")
            cluster_metrics_safe = cluster_metrics.astype(object).where(pd.notnull(cluster_metrics), None).to_dict(orient="records")
            
            return {
                "success": True,
                "data": {
                    "segmented_customers": df_segmented_safe,
                    "cluster_metrics": cluster_metrics_safe
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def forecast_sales(self, file_path: str):
        """Run sales forecasting on uploaded file"""
        try:
            if file_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            else:
                df = pd.read_csv(file_path)
            
            forecast_results = sales_forecast_pipeline(df)
            
            # Convert outputs safely
            top10_safe = forecast_results['top10_products'].astype(object).where(pd.notnull(forecast_results['top10_products']), None).to_dict(orient="records")
            demand_quarter_safe = forecast_results['demand_quarter'].astype(object).where(pd.notnull(forecast_results['demand_quarter']), None).to_dict(orient="records")
            mae_safe = float(forecast_results['mae']) if isinstance(forecast_results['mae'], (np.floating, np.integer)) else forecast_results['mae']
            
            # Compute total forecasted sales
            total_forecasted_sales = sum(item['forecasted_sales'] for item in demand_quarter_safe)
            
            # Compute average daily sales (assuming next quarter ~90 days)
            average_daily_sales = total_forecasted_sales / 90
            
            return {
                "success": True,
                "data": {
                    "top10_products": top10_safe,
                    "demand_quarter": demand_quarter_safe,
                    "mae": mae_safe,
                    "forecast_summary": {
                        "total_forecasted_sales": total_forecasted_sales,
                        "average_daily_sales": average_daily_sales
                    }
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _categorize_churn_risk(self, df):
        """Categorize customers by churn risk"""
        bins = [0, 0.33, 0.66, 1.0]
        labels = ["Low", "Medium", "High"]
        df['churn_risk'] = pd.cut(df['churn_probability'], bins=bins, labels=labels)
        return df
    
    def _churn_rate_trends(self, df):
        """Compute churn rate trends by month"""
        df['last_purchase_month'] = df['last_purchase_date'].dt.to_period('M')
        trend = df.groupby('last_purchase_month')['churn_probability'].mean().reset_index()
        trend['last_purchase_month'] = trend['last_purchase_month'].astype(str)
        trend['churn_probability'] = trend['churn_probability'].astype(float)
        return trend

# Global instance
ml_service = MLService()
