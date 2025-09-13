# Weather Dashboard

A personal weather monitoring system that collects detailed weather data for desert valley conditions and displays it through an interactive dashboard.

## Project Overview

This project creates an automated pipeline to collect, process, and visualize weather data using AWS Lambda, BigQuery, and Looker Studio. Born out of a passion for understanding the unique weather patterns of desert valley living, this system provides detailed insights beyond what standard weather apps offer.

## Architecture

```
CloudWatch Events (Daily Trigger) → AWS Lambda → Tomorrow.io API → S3 (Parquet) → BigQuery → Looker Studio Dashboard
                
```

## The Story Behind This Project

Living in a desert valley means experiencing weather that can be dramatically different from what general weather forecasts predict. Desert valleys have unique microclimates with:
- Extreme temperature swings between day and night
- Wind patterns that change based on valley topography  
- Humidity levels that can vary significantly from surrounding areas
- Temperature inversions and other valley-specific phenomena

Standard weather apps often miss these nuances. This project was built to capture and analyze the detailed weather patterns specific to my location, helping me better understand and prepare for the unique conditions of desert valley weather.


## Project Structure

```
├── lambda_function.py         # Main Lambda function for data collection
├── requirements.txt           # Python dependencies
├── schema/
│   └── bigquery_schema.json   # BigQuery table schema definition
├── sql/
│   ├── ddl/                   # Table creation scripts
│   ├── queries/               # Common analysis queries
├── .env                       # Environment variables for accessing AWS and API keys
└── README.md                  # This file
```

## Setup Instructions

### Prerequisites

- Tomorrow.io API key
- AWS Account with Lambda, S3, and CloudWatch permissions
- Google Cloud Project with BigQuery enabled
- Looker Studio access

### AWS Configuration

1. Create S3 Bucket

2. Deploy Lambda Function

3. Set Environment Variables

4. Create CloudWatch Event Rule

### BigQuery Setup

1. Create dataset and table using the provided schema

2. Set up data transfer from S3 to BigQuery (daily schedule).

3. Run queries to get necessary columns and transformations/aggregates.

### Looker Studio Dashboard

1. Connect Looker Studio to your BigQuery dataset

2. Create visualizations for:
   - Temperature trends over time
   - Humidity and precipitation patterns
   - Wind speed and direction analysis
   - Daily/weekly weather summaries

## Design Decisions

### Why Parquet Over Raw JSON?

While the initial data from Tomorrow.io API comes as JSON, I chose to export it as Parquet files for several key reasons:

- **Storage Efficiency**: Parquet's columnar format significantly reduces file size compared to JSON, important when collecting data multiple times daily over months/years
- **Query Performance**: BigQuery processes Parquet files much faster than JSON, especially for analytical queries across date ranges
- **Schema Evolution**: Parquet handles schema changes gracefully, allowing me to add new weather metrics without breaking existing data
- **Cost Optimization**: Smaller file sizes mean lower S3 storage costs and faster BigQuery data transfer

### Simple Python Preprocessing

The weather data preprocessing is handled entirely within the Lambda function using Python rather than a separate data processing service because:

- **Data Simplicity**: Tomorrow.io returns clean, structured JSON that requires minimal transformation
- **Small Data Volume**: Daily weather snapshots are small enough to process efficiently in Lambda's execution environment  
- **Reduced Complexity**: Keeping preprocessing in the same function eliminates the need for additional AWS services and potential failure points
- **Cost Effectiveness**: Lambda's pay-per-execution model is perfect for lightweight daily processing tasks

### Skipping Athena

While AWS Athena might seem like a natural fit for querying S3 data, I chose to go directly from S3 to BigQuery because:

- **Avoiding Redundancy**: Adding Athena would create an unnecessary intermediate step - I'd still need BigQuery for Looker Studio integration
- **Single Source of Truth**: Having all processed data in BigQuery eliminates the complexity of maintaining data consistency across multiple query engines
- **Advanced Analytics**: BigQuery offers more sophisticated analytical functions and better integration with Google's visualization tools
- **Simplified Architecture**: Fewer moving parts means fewer things that can break and easier maintenance

Data is collected daily and stored with full timestamp precision for detailed temporal analysis.

## Contributing

This is a personal project, but feel free to fork and adapt for your own location-specific weather monitoring needs!

## License

MIT License - Feel free to use this for your own weather monitoring adventures.