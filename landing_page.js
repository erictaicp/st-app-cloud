import React from 'react';

const Feature = ({ icon, title, description }) => (
  <div className="feature flex flex-col items-center p-6 bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105">
    <div className="text-4xl mb-4">{icon}</div>
    <h3 className="text-lg font-bold text-gray-800">{title}</h3>
    <p className="mt-2 text-sm text-gray-600 text-center">{description}</p>
  </div>
);

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center">
          <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl md:text-6xl" role="heading" aria-level="1">
            Project <span className="text-indigo-600">Alchemist</span>
          </h1>
          <p className="mt-3 max-w-2xl mx-auto text-xl text-gray-500">
            Revolutionizing document and order management with AI-powered automation
          </p>
        </div>

        <div className="mt-12">
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            <Feature
              icon="🧠"
              title="AI Agent"
              description="Intelligent AI agent powered by GPT-4 for complex tasks, queries, and document processing workflows."
            />
            <Feature
              icon="📊"
              title="Order Management"
              description="Streamlined order placement, status tracking, and document submission with real-time updates."
            />
            <Feature
              icon="📄"
              title="Document Processing"
              description="AI-driven document validation, type recognition, and field extraction for various document types."
            />
            <Feature
              icon="🔍"
              title="Content Checker"
              description="AI-powered checking system with customizable rules for validating orders and documents across the same order ID."
            />
            <Feature
              icon="🚀"
              title="Extraction Express"
              description="Rapid document validation and key field extraction tool for efficient data processing."
            />
            <Feature
              icon="📚"
              title="Chase Book"
              description="Comprehensive order management system for viewing, editing, and tracking all orders in one place."
            />
            <Feature
              icon="🔔"
              title="Smart Reminders"
              description="Automated reminders via email and WhatsApp for timely document submission and updates."
            />
            <Feature
              icon="👥"
              title="Role-Based Access"
              description="Tailored functionalities for admins and clients with secure access control and user management."
            />
            <Feature
              icon="🌐"
              title="Multi-Country Support"
              description="Configurable settings for different countries with country-specific document types and key fields."
            />
            <Feature
              icon="📱"
              title="Multi-Channel Integration"
              description="Seamless communication through various channels like email, WhatsApp, and web portal using a unified API."
            />
            <Feature
              icon="📈"
              title="Market Researcher"
              description="AI-powered online market research agent to gather information about interested companies and industry trends."
            />
            <Feature
              icon="🧙‍♂️"
              title="Data Wizard"
              description="Advanced data visualization and insights tool for transforming raw data into actionable intelligence."
            />
          </div>
        </div>

        <div className="mt-16 text-center">
          <h2 className="text-3xl font-bold text-gray-900">Supported Document Types</h2>
          <p className="mt-2 text-lg text-gray-600">
            Certificate of Origin, Commercial Invoice, Proof of Payment, Contract, Bill of Lading, and more.
          </p>
        </div>

        <div className="mt-16 text-center">
          <h2 className="text-3xl font-bold text-gray-900">Cutting-Edge Tech Stack</h2>
          <p className="mt-2 text-lg text-gray-600">
            Python 3.10, React, FastAPI, MongoDB, Azure Blob Storage, Langchain with GPT-4
          </p>
        </div>

        <div className="mt-16 text-center">
          <h2 className="text-3xl font-bold text-gray-900">What Our Users Say</h2>
          <div className="mt-6 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <p className="text-gray-600 italic">"Project Alchemist has revolutionized our document management process. It's like having a team of experts working 24/7!"</p>
              <p className="mt-4 font-semibold">- Sarah J., Operations Manager</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <p className="text-gray-600 italic">"The AI-powered content checker has significantly reduced errors and improved our compliance. It's a game-changer!"</p>
              <p className="mt-4 font-semibold">- Michael L., Compliance Officer</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <p className="text-gray-600 italic">"The multi-country support and data visualization tools have given us insights we never had before. Highly recommended!"</p>
              <p className="mt-4 font-semibold">- Elena R., Global Logistics Director</p>
            </div>
          </div>
        </div>

        <div className="mt-16 text-center">
          <h2 className="text-3xl font-bold text-gray-900">Ready to Transform Your Workflow?</h2>
          <p className="mt-4 text-xl text-gray-600">Join the AI revolution in document and order management today!</p>
          <button className="mt-8 px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 md:py-4 md:text-lg md:px-10">
            Get Started
          </button>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;