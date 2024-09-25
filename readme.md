![Python Version](https://img.shields.io/badge/python-3.10-blue)

## Definition
**Order**: A request for a product or service that contains a batch of documents.

## Objective
Project Alchemist aims to mimic the process of human handling document and order management. The project is designed to equip unlimited tools and AI decision-making to automate tasks such as reminders for document submission, validate the documents upon submission, and provide a platform for clients to upload documents and check the status of their orders.

## Table of Contents

- [Definition](#definition)
- [Objective](#objective)
- [Table of Contents](#table-of-contents)
- [Problem Statement](#problem-statement)
- [Features](#features)
  - [General Features](#general-features)
  - [T4S Features](#t4s-features)
  - [Air8 Features](#air8-features)
  - [Bonus Features:](#bonus-features)
- [Communication Channels](#communication-channels)
- [User Roles](#user-roles)
- [Prompt Examples](#prompt-examples)
- [Supported Document Types](#supported-document-types)
- [Architecture](#architecture)
- [Development Roadmap](#development-roadmap)
  - [Completed](#completed)
  - [In Progress](#in-progress)
  - [Planned](#planned)

## Problem Statement

Our client handles a high volume of orders that require document submission. The challenge is to automate reminders for document submission, validate the documents upon submission, and provide a platform for clients to upload documents and check the status of their orders.

## Features

### General Features
- **Send Reminder**: Automated reminders are sent to users to ensure timely document submission.
- **Document Upload**: Users can easily upload necessary documents for each order through a user-friendly interface.
- **Document Type Validation**:
  - Each uploaded document undergoes thorough validation to ensure it matches the expected file type.
  - Successful AI validation forwards the document to a human reviewer.
  - If AI validation fails, users are notified and prompted to re-upload the document.
  - Human final approval (Streamlit interface).
- **Multi-country Support**:
  - Configurable settings for different countries (e.g., China, India)
  - Country-specific document types and key fields
- **Document Field Validation**:
  - Extract field values from documents.
- **Order Placement**: Users can seamlessly place orders through the front-end interface.
- **Status Check**: Users can check the status of their orders at any time thru Chat Interface.
- **Checker Feature**:
  - AI checks information for the same order ID.
  - Customized rules determine the status of the order.
  - Checking system with scoring

### T4S Features

- **Supported Document Types**: Includes various document types such as Certificate of Origin, Commercial Invoice, Proof of Payment, Contract, Bill of Lading, and more.
- **Document Type Family Mapping**: Maps various document types to their respective families for better categorization and processing.
- **Selected Fields Extraction**: Extracts specific fields from documents based on their type for detailed analysis and validation.
- **Database Integration**: Uses T4S API and Service Bus

### Air8 Features

- **Possible Document Types**: Invoice, Purchase Order, Delivery Document
- **Document Family and Key Fields**: Defines document families and key fields for various document types to ensure accurate data extraction and validation.
- **Country-Specific Configurations**: Supports different document types and key fields for China and India, allowing for localized document processing.
- **Check Rules**: Implements a set of rules to compare and validate document fields, ensuring consistency and accuracy across related documents.

### Bonus Features
- **Market Researcher**: Online market research agent to gather information about interested companies.
- **Company Research & News**: Comprehensive company research and news gathering tool.

## Communication Channels

- **Email**: Used for receiving reminders.
- **WhatsApp**: Used for receiving reminders and Q&A.
- **Web Portal**: Used for placing chase requests, uploading documents, and checking order status.

## User Roles

- **ADMIN**:
  - Create records.
  - Send reminders to all or specific clients.
  - Validate documents.
  - Extract contents.
  - Query the status of all orders in the database.
- **CLIENT**:
  - Query the status of their own orders.
  - Request a submission link.

## Prompt Examples

- To create a record:
  - `Could you create a record for me? Order ID is {xyz001}, email is {xxx@lifung.com}, WhatsApp is {1234567789}, etc.`
- To send reminders:
  - `Send reminders to all clients for document submission.`
  - `Send a reminder to the client whose case ID is {xyz001}.`
- To validate documents:
  - `It's triggered automatically whenever a document is submitted.`
- To extract content:
  - `Extract the text from the document for me. The file path is {/doc_needed_extracted.pdf}.`
- To query:
  - `Tell me the onboarding status of the case with order ID {xyz001}.`
  - `What document is missing for the case {xyz001}?`
- To get a submission URL:
  - `Give me the submission link for my case with ID {xyz001}.`

## Supported Document Types

The system supports various document types including Certificate of Origin, Commercial Invoice, Proof of Payment, Contract, Bill of Lading, Delivery Note, Packing List, Customs Clearance, Business License, Production Record, Warehouse Record, and Certification Record.

## Architecture

- **Frontend**: Streamlit with React components
- **Backend**: Python & FastAPI
- **Database**: MongoDB
- **AI/ML**: Langchain with GPT-4
- **WhatsApp**: Serveo and Pywa
- **File Storage**: Azure Blob Storage

## Development Roadmap

### Completed
- [x] Basic document upload and validation
- [x] Automated email reminders
- [x] WhatsApp integration (Testing Env)
- [x] Order placement through the front end
- [x] Status check functionality for users
- [x] WhatsApp integration (Business Env)
- [x] Document field key value extraction
- [x] Human document validation interface
- [x] Platform integration with API
- [x] Q&A on order status and statistics
- [x] Multi-country configuration support
- [x] Checker feature across the same order ID
  - [x] Customized rules
- [x] Landing page with React components
- [x] Chase Book feature for managing orders
- [x] Document upload portal with multi-threading support
- [x] Company research and news gathering tool
- [x] Order status tracking with statistics
- [x] Content checker for document validation
- [x] Human validation interface for documents
- [x] Extraction Express for document validation and field extraction

### In Progress
- [ ] Market research: Adding more sources and refactoring output results into sections
- [ ] Data Wizard feature for advanced data manipulation
- [ ] Supplier search feature with AI agent