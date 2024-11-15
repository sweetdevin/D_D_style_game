import asyncio
# Asynchronous recursive function
async def async_recursive_function(count):
    if count <= 0:
        print("End of recursion.")
        return
    print(f"Recursion count: {count}")
    
    # Awaiting user input asynchronously
    user_input = await asyncio.to_thread(input, "Do you want to continue? (y/n): ")  # Non-blocking input
    
    if user_input.lower() == 'y':
        await async_recursive_function(count - 1)  # Recurse asynchronously
    else:
        print("Stopping recursion.")

# Main async function to start the recursion
async def main():
    await async_recursive_function(5)  # Start recursion with a count of 5

# Run the main function in the asyncio event loop
asyncio.run(main())
