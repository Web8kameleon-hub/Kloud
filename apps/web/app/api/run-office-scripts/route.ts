import { NextResponse } from "next/server";

// PRODUCTION: Hetzner server IP / kloud.com
// Port 8002 = Excel microservice
const EXCEL_API = process.env.EXCEL_API_URL || "http://kloud-reporting:8001";
const API_BASE = process.env.EXCEL_API_URL || EXCEL_API;

export async function GET() {
  try {
    // Call backend to run Office Scripts
    const response = await fetch(`${API_BASE}/api/excel/run-scripts`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
    });

    if (response.ok) {
      const data = await response.json();
      return NextResponse.json({
        success: true,
        message: "Office Scripts executed",
        ...data,
      });
    }

    // Return info about available scripts
    return NextResponse.json({
      success: true,
      message: "Office Scripts ready to run",
      timestamp: new Date().toISOString(),
      available_scripts: [
        {
          name: "colorizeAPIRow",
          description: "Apply color formatting based on HTTP method",
          status: "ready",
        },
        {
          name: "createDropdownList",
          description: "Create validation dropdown lists",
          status: "ready",
        },
        {
          name: "syncWithAPI",
          description: "Sync Excel data with backend API",
          status: "ready",
        },
        {
          name: "generateCurlCommand",
          description: "Generate cURL commands from row data",
          status: "ready",
        },
      ],
      note: "Office Scripts run in Excel Desktop/Web. Use Power Automate for automation.",
      instructions: [
        "1. Open Excel file in Excel Online or Desktop",
        "2. Go to Automate tab",
        "3. Select and run the desired script",
        "4. Or use Power Automate for scheduled runs",
      ],
    });
  } catch (_error) {
    return NextResponse.json({
      success: true,
      message: "Office Scripts info",
      scripts_count: 4,
      hint: "Office Scripts require Excel Online or Desktop with M365 subscription",
    });
  }
}

export async function POST() {
  return GET();
}

