import React, { useState } from 'react';
import axios from 'axios';
import { ShieldAlert, ShieldCheck, Zap } from 'lucide-react';

const AuditPage = () => {
  const [formData, setFormData] = useState({ avg_current: 0, house_size: 1, zero_days: 0 });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handlePredict = async () => {
    setLoading(true);
    try {
      // Connects to your FastAPI /predict endpoint
      const response = await axios.post('http://127.0.0.1:8000/predict', formData);
      setResult(response.data);
    } catch (error) {
      alert("Backend not reachable. Make sure FastAPI is running!");
    }
    setLoading(false);
  };

  return (
    <div className="max-w-xl mx-auto p-6 bg-gray-50 min-h-screen">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-blue-900">⚡ SmartAudit AI</h1>
        <p className="text-gray-600">Enter field observations for instant theft analysis</p>
      </header>

      <div className="bg-white p-8 rounded-2xl shadow-lg space-y-6">
        {/* Input 1: Current */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Measured Current (kWh)</label>
          <input type="number" className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
            onChange={(e) => setFormData({...formData, avg_current: parseFloat(e.target.value)})} />
        </div>

        {/* Input 2: House Size */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Property Size (Scale 1-5)</label>
          <input type="range" min="1" max="5" className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            onChange={(e) => setFormData({...formData, house_size: parseInt(e.target.value)})} />
          <div className="flex justify-between text-xs text-gray-500 px-1 mt-1">
            <span>Small</span><span>Medium</span><span>Mansion</span>
          </div>
        </div>

        {/* Input 3: Zero Days */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Zero Consumption Days</label>
          <input type="number" className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
            onChange={(e) => setFormData({...formData, zero_days: parseInt(e.target.value)})} />
        </div>

        <button onClick={handlePredict} disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-xl transition duration-200">
          {loading ? "Analyzing..." : "RUN AI PREDICTION"}
        </button>
      </div>

      {/* Result Card */}
      {result && (
        <div className={`mt-8 p-6 rounded-2xl border-2 flex items-center space-x-4 ${
          result.prediction === 1 ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'
        }`}>
          {result.prediction === 1 ? <ShieldAlert size={48} className="text-red-600" /> : <ShieldCheck size={48} className="text-green-600" />}
          <div>
            <h2 className="text-xl font-bold">{result.status}</h2>
            <p className="text-sm font-semibold text-gray-600">Risk Confidence: {result.risk_score}%</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default AuditPage;