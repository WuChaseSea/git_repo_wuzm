import argparse
import asyncio

from src.agent.xiaoling import XIAOLING
from src.logger import logger


async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run ToolCall Agent with a prompt")
    parser.add_argument(
        "--prompt", type=str, required=False, help="Input prompt for the agent"
    )
    args = parser.parse_args()
    # agent = ToolcallAgent()
    xiaoling = XIAOLING(mode="知性搭子")
    try:
        # Use commmand line prompt if provided, otherwise ask for input
        prompt = args.prompt if args.prompt else input("Enter you prompt: ")
        if not prompt.strip():
            logger.warning("Empty prompt provided.")
            return
        
        logger.warning("Processing your request...")
        
        await xiaoling.run(prompt)
        logger.info("Request processing completed.")
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    finally:
        # Ensure agent resources are cleaned up before exiting
        await xiaoling.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
