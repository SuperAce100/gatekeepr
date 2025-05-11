import chainlit as cl


@cl.on_message
async def on_message(message: cl.Message):
    # Your custom logic goes here...

    # Send a response back to the user
    await cl.Message(
        content=f"Received: {message.content}",
    ).send()


if __name__ == "__main__":
    # cl.run_app(on_message)
    print("Running...")
