// app/api/chat/[userId]/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ userId: string }> }
) {
  try {
    const { userId } = await params;
    const { message, conversation_id } = await request.json();

    // Verify authentication token exists
    const authToken = request.cookies.get('auth_token')?.value;

    if (!authToken) {
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }

    // Forward the request to the backend chat API
    const backendResponse = await fetch(`${process.env.BACKEND_URL || 'http://localhost:8000'}/api/chat/${userId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`,
      },
      body: JSON.stringify({
        message: message,
        conversation_id: conversation_id
      }),
      redirect: 'follow'
    });

    if (!backendResponse.ok) {
      const errorData = await backendResponse.json().catch(() => ({ error: `HTTP error! status: ${backendResponse.status}` }));
      console.error('Backend API Error:', backendResponse.status, errorData);
      return NextResponse.json(
        { error: `Backend API Error: ${backendResponse.status}`, details: errorData },
        { status: backendResponse.status }
      );
    }

    const data = await backendResponse.json();
    return NextResponse.json(data);

  } catch (error) {
    console.error('Error in chat API:', error);
    return NextResponse.json(
      { error: 'Failed to process chat message', details: (error as Error).message },
      { status: 500 }
    );
  }
}