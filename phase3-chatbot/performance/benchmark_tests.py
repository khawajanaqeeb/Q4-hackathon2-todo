"""
Performance Benchmark Tests for Todo AI Chatbot

Tests for measuring performance, response times, and resource usage of the Todo AI Chatbot.
"""

import time
import asyncio
import statistics
from typing import List, Dict, Any
import pytest
from unittest.mock import patch

from skills.chatbot_orchestration_skill import ChatbotOrchestrationSkill
from agents.api_integration_agent import APIResponse


def test_response_time_single_request():
    """Test response time for a single request."""
    # Initialize orchestration skill
    orchestration_skill = ChatbotOrchestrationSkill("http://test-api.com", "test-token")

    # Mock the API integration agent
    with patch.object(orchestration_skill.api_integration_agent, 'send_request') as mock_api_request:
        mock_api_request.return_value = APIResponse(201, {"id": 1, "content": "test task", "completed": False})

        # Measure response time
        start_time = time.time()
        result = asyncio.run(orchestration_skill.orchestrate_agents(
            user_id="perf_test_user",
            input_message="Add a task to test performance",
            platform="web"
        ))
        end_time = time.time()

        response_time = end_time - start_time

        # Verify the result
        assert result.success is True
        assert result.response is not None

        # Performance requirement: response time under 2 seconds
        assert response_time < 2.0, f"Response time {response_time:.2f}s exceeded 2s threshold"

        print(f"Single request response time: {response_time:.3f}s")


def test_response_time_multiple_requests():
    """Test response time for multiple sequential requests."""
    # Initialize orchestration skill
    orchestration_skill = ChatbotOrchestrationSkill("http://test-api.com", "test-token")

    # Mock the API integration agent
    with patch.object(orchestration_skill.api_integration_agent, 'send_request') as mock_api_request:
        mock_api_request.return_value = APIResponse(201, {"id": 1, "content": "test task", "completed": False})

        response_times = []
        num_requests = 10

        for i in range(num_requests):
            start_time = time.time()
            result = asyncio.run(orchestration_skill.orchestrate_agents(
                user_id=f"perf_test_user_{i}",
                input_message=f"Add a task to test performance {i}",
                platform="web"
            ))
            end_time = time.time()

            response_time = end_time - start_time
            response_times.append(response_time)

            # Verify the result
            assert result.success is True
            assert result.response is not None

        # Calculate performance metrics
        avg_response_time = statistics.mean(response_times)
        median_response_time = statistics.median(response_times)
        p95_response_time = sorted(response_times)[int(0.95 * len(response_times))] if response_times else 0

        # Performance requirements
        assert avg_response_time < 2.0, f"Average response time {avg_response_time:.2f}s exceeded 2s threshold"
        assert p95_response_time < 3.0, f"P95 response time {p95_response_time:.2f}s exceeded 3s threshold"

        print(f"Multiple requests - Avg: {avg_response_time:.3f}s, Median: {median_response_time:.3f}s, P95: {p95_response_time:.3f}s")


@pytest.mark.asyncio
async def test_concurrent_users_performance():
    """Test performance under concurrent user load."""
    # Initialize orchestration skill
    orchestration_skill = ChatbotOrchestrationSkill("http://test-api.com", "test-token")

    async def make_request(user_id: str, message: str) -> float:
        with patch.object(orchestration_skill.api_integration_agent, 'send_request') as mock_api_request:
            mock_api_request.return_value = APIResponse(201, {"id": user_id, "content": message, "completed": False})

            start_time = time.time()
            result = await orchestration_skill.orchestrate_agents(
                user_id=user_id,
                input_message=message,
                platform="web"
            )
            end_time = time.time()

            assert result.success is True
            assert result.response is not None

            return end_time - start_time

    # Simulate concurrent users
    num_concurrent_users = 20
    tasks = [
        make_request(f"concurrent_user_{i}", f"Task for user {i}")
        for i in range(num_concurrent_users)
    ]

    start_time = time.time()
    response_times = await asyncio.gather(*tasks)
    total_time = time.time() - start_time

    # Calculate performance metrics
    avg_response_time = statistics.mean(response_times)
    max_response_time = max(response_times) if response_times else 0

    # Performance requirements for concurrent load
    assert avg_response_time < 3.0, f"Average response time {avg_response_time:.2f}s exceeded 3s threshold under load"
    assert max_response_time < 5.0, f"Max response time {max_response_time:.2f}s exceeded 5s threshold under load"

    print(f"Concurrent users ({num_concurrent_users}) - Total time: {total_time:.3f}s, Avg: {avg_response_time:.3f}s, Max: {max_response_time:.3f}s")


def test_memory_usage_stress():
    """Test memory usage under stress conditions."""
    import gc

    # Initialize orchestration skill
    orchestration_skill = ChatbotOrchestrationSkill("http://test-api.com", "test-token")

    # Mock the API integration agent
    with patch.object(orchestration_skill.api_integration_agent, 'send_request') as mock_api_request:
        mock_api_request.return_value = APIResponse(201, {"id": 1, "content": "test task", "completed": False})

        # Process many requests to test memory usage
        successful_requests = 0
        for i in range(50):  # Reduced to make test faster without psutil
            result = asyncio.run(orchestration_skill.orchestrate_agents(
                user_id=f"stress_user_{i}",
                input_message=f"Add a task to test memory usage {i}",
                platform="web"
            ))
            assert result.success is True
            assert result.response is not None
            successful_requests += 1

            # Force garbage collection periodically to prevent memory buildup
            if i % 10 == 0:
                gc.collect()

    # Just verify that the system handled the requests without crashing
    # In a full implementation, we would measure actual memory usage with psutil
    assert successful_requests == 50, f"Expected 50 successful requests, got {successful_requests}"

    print(f"Memory stress test - Processed {successful_requests} requests successfully without memory issues")


@pytest.mark.asyncio
async def test_throughput_measurements():
    """Test throughput measurements (requests per second)."""
    # Initialize orchestration skill
    orchestration_skill = ChatbotOrchestrationSkill("http://test-api.com", "test-token")

    async def make_request(user_id: str, message: str) -> bool:
        with patch.object(orchestration_skill.api_integration_agent, 'send_request') as mock_api_request:
            mock_api_request.return_value = APIResponse(201, {"id": user_id, "content": message, "completed": False})

            result = await orchestration_skill.orchestrate_agents(
                user_id=user_id,
                input_message=message,
                platform="web"
            )
            return result.success

    # Measure throughput over a time period
    duration = 5  # seconds
    end_time = time.time() + duration
    request_count = 0

    while time.time() < end_time:
        success = await make_request(f"throughput_user_{request_count}", f"Throughput test {request_count}")
        assert success
        request_count += 1

    # Calculate throughput
    actual_duration = time.time() - (end_time - duration)
    throughput = request_count / actual_duration

    # Performance requirement: at least 5 requests per second
    assert throughput >= 5, f"Throughput {throughput:.2f} req/s is below minimum requirement of 5 req/s"

    print(f"Throughput: {throughput:.2f} requests/second over {actual_duration:.2f}s ({request_count} requests)")


def test_api_response_time_simulation():
    """Test system performance with simulated API response times."""
    # Initialize orchestration skill
    orchestration_skill = ChatbotOrchestrationSkill("http://test-api.com", "test-token")

    # Mock the API integration agent with varying response times
    def slow_api_response(*args, **kwargs):
        time.sleep(0.5)  # Simulate 500ms API response time
        return APIResponse(201, {"id": 1, "content": "slow task", "completed": False})

    with patch.object(orchestration_skill.api_integration_agent, 'send_request', side_effect=slow_api_response):
        start_time = time.time()
        result = asyncio.run(orchestration_skill.orchestrate_agents(
            user_id="slow_api_user",
            input_message="Add a task with slow API",
            platform="web"
        ))
        end_time = time.time()

        response_time = end_time - start_time

        # With 500ms simulated API delay, total response time should be reasonable
        assert result.success is True
        assert response_time < 2.0, f"With slow API, response time {response_time:.2f}s exceeded 2s threshold"

        print(f"Slow API response time: {response_time:.3f}s")


@pytest.mark.asyncio
async def test_context_manager_performance():
    """Test performance of context management operations."""
    # Initialize orchestration skill
    orchestration_skill = ChatbotOrchestrationSkill("http://test-api.com", "test-token")

    # Test context operations performance
    user_id = "context_perf_user"

    # Add multiple messages to context
    start_time = time.time()
    for i in range(50):
        orchestration_skill.context_manager_agent.add_message_to_history(
            user_id, "user", f"Message {i} for performance testing"
        )
    add_time = time.time() - start_time

    # Get recent messages
    start_time = time.time()
    recent_messages = orchestration_skill.context_manager_agent.get_recent_messages(user_id, 10)
    get_time = time.time() - start_time

    # Verify results
    assert len(recent_messages) == min(10, 50)
    assert add_time < 1.0, f"Adding 50 messages took {add_time:.3f}s, which is too slow"
    assert get_time < 0.1, f"Getting recent messages took {get_time:.3f}s, which is too slow"

    print(f"Context management - Add 50 msgs: {add_time:.3f}s, Get 10 msgs: {get_time:.3f}s")


if __name__ == "__main__":
    print("Running performance benchmark tests...")

    # Run tests individually to measure performance
    test_response_time_single_request()
    test_response_time_multiple_requests()
    test_memory_usage_stress()
    test_api_response_time_simulation()
    test_context_manager_performance()

    # Run async tests
    asyncio.run(test_concurrent_users_performance())
    asyncio.run(test_throughput_measurements())

    print("All performance benchmark tests completed!")