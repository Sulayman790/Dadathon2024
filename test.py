from anthropic import AnthropicBedrock
input_text = "What are the best stocks to buy if I like environment? Please return the ticker at the very end."
client = AnthropicBedrock(
    # Authenticate by either providing the keys below or use the default AWS credential providers, such as
    # using ~/.aws/credentials or the "AWS_SECRET_ACCESS_KEY" and "AWS_ACCESS_KEY_ID" environment variables.
    aws_access_key="AKIAR2QID37NBSCXNSWA",
    aws_secret_key="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",

    # aws_region changes the aws region to which the request is made. By default, we read AWS_REGION,
    # and if that's not present, we default to us-east-1. Note that we do not read ~/.aws/config for the region.
    aws_region="us-west-2",
)

message = client.messages.create(
    model="anthropic.claude-3-sonnet-20240229-v1:0",
    max_tokens=256,
    messages=[{"role": "user", "content": input_text}],
)
texte = message.content[0].text
print(texte)