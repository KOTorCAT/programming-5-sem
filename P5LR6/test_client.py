"""
Тестовый клиент для проверки работы Currency Rate Observer
"""
import asyncio
import json
import websockets
import sys
from typing import Any, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_websocket_client(uri: str = "ws://localhost:8888/ws") -> None:
    """
    Тестовый клиент для проверки WebSocket соединения
    """
    try:
        async with websockets.connect(uri) as websocket:
            logger.info(f"Connected to {uri}")
            
            # Получаем приветственное сообщение
            welcome_message = await websocket.recv()
            welcome_data = json.loads(welcome_message)
            
            logger.info(f"Welcome message: {welcome_data.get('message')}")
            logger.info(f"Client ID: {welcome_data.get('client_id')}")
            
            # Подписываемся на валюты
            subscribe_message = {
                "type": "subscribe",
                "currencies": ["USD", "EUR", "GBP"]
            }
            await websocket.send(json.dumps(subscribe_message))
            logger.info("Subscribed to USD, EUR, GBP")
            
            # Запрашиваем текущие курсы
            get_rates_message = {"type": "get_rates"}
            await websocket.send(json.dumps(get_rates_message))
            logger.info("Requested current rates")
            
            # Слушаем сообщения в течение 30 секунд
            logger.info("Listening for messages for 30 seconds...")
            
            for i in range(30):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    
                    message_type = data.get("type", "unknown")
                    
                    if message_type == "rates_updated":
                        logger.info(f"Rate update received with {len(data.get('changes', []))} changes")
                        for change in data.get("changes", []):
                            code = change.get("code")
                            old_rate = change.get("old_rate")
                            new_rate = change.get("new_rate")
                            logger.info(f"  {code}: {old_rate} → {new_rate}")
                    
                    elif message_type == "current_rates":
                        logger.info(f"Current rates received for {len(data.get('rates', {}))} currencies")
                    
                    elif message_type == "subscription_updated":
                        logger.info(f"Subscription updated: {data.get('currencies')}")
                    
                    else:
                        logger.info(f"Received {message_type}: {data.get('message', 'No message')}")
                        
                except asyncio.TimeoutError:
                    # Отправляем ping каждые 5 секунд
                    if i % 5 == 0:
                        ping_message = {"type": "ping"}
                        await websocket.send(json.dumps(ping_message))
                    continue
                    
            logger.info("Test completed successfully")
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)


async def test_multiple_clients(num_clients: int = 3) -> None:
    """
    Тест с несколькими одновременными клиентами
    """
    logger.info(f"Testing with {num_clients} simultaneous clients...")
    
    tasks = []
    for i in range(num_clients):
        task = asyncio.create_task(
            test_single_client(f"TestClient-{i+1}")
        )
        tasks.append(task)
        await asyncio.sleep(0.5)  # Небольшая задержка между подключениями
    
    await asyncio.gather(*tasks)
    logger.info("Multiple client test completed")


async def test_single_client(client_name: str) -> None:
    """
    Тест одного клиента
    """
    try:
        async with websockets.connect("ws://localhost:8888/ws") as websocket:
            # Получаем приветственное сообщение
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            client_id = welcome_data.get("client_id")
            
            logger.info(f"{client_name} connected with ID: {client_id}")
            
            # Слушаем 3 сообщения
            for i in range(3):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(message)
                    
                    if data.get("type") == "rates_updated":
                        logger.info(f"{client_name} received rate update")
                    
                except asyncio.TimeoutError:
                    logger.warning(f"{client_name} timed out waiting for message")
                    break
            
            logger.info(f"{client_name} disconnected")
            
    except Exception as e:
        logger.error(f"{client_name} failed: {e}")


async def test_simulated_changes() -> None:
    """
    Тест имитации изменений (работает только в тестовом режиме сервера)
    """
    try:
        async with websockets.connect("ws://localhost:8888/ws") as websocket:
            # Получаем приветственное сообщение
            await websocket.recv()
            
            logger.info("Testing simulated rate changes...")
            
            # Запрашиваем имитацию изменения
            simulate_message = {"type": "simulate_change"}
            await websocket.send(json.dumps(simulate_message))
            logger.info("Requested rate change simulation")
            
            # Ждем ответ
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            
            if response_data.get("type") == "simulation_started":
                logger.info("Simulation started successfully")
                
                # Ждем обновления курсов
                for i in range(3):
                    try:
                        update = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                        update_data = json.loads(update)
                        
                        if update_data.get("type") == "rates_updated":
                            logger.info("Received simulated rate update")
                            if update_data.get("simulated"):
                                logger.info("✓ Confirmed: This is a simulated update")
                            break
                            
                    except asyncio.TimeoutError:
                        logger.warning("Timeout waiting for simulated update")
                        break
            else:
                logger.error(f"Unexpected response: {response_data}")
                
    except Exception as e:
        logger.error(f"Simulation test failed: {e}")


def run_basic_test() -> None:
    """Запуск базового теста"""
    logger.info("Running basic WebSocket test...")
    asyncio.run(test_websocket_client())


def run_multiple_clients_test() -> None:
    """Запуск теста с несколькими клиентами"""
    logger.info("Running multiple clients test...")
    asyncio.run(test_multiple_clients(3))


def run_simulation_test() -> None:
    """Запуск теста имитации изменений"""
    logger.info("Running simulation test...")
    asyncio.run(test_simulated_changes())


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test client for Currency Rate Observer")
    parser.add_argument(
        "--test", 
        choices=["basic", "multiple", "simulation", "all"],
        default="basic",
        help="Type of test to run"
    )
    
    args = parser.parse_args()
    
    try:
        if args.test == "basic":
            run_basic_test()
        elif args.test == "multiple":
            run_multiple_clients_test()
        elif args.test == "simulation":
            run_simulation_test()
        elif args.test == "all":
            run_basic_test()
            print("\n" + "="*50 + "\n")
            run_multiple_clients_test()
            print("\n" + "="*50 + "\n")
            run_simulation_test()
            
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)