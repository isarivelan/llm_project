import logging

    
def total_cost_calc(all_prompt_tokens, all_completion_tokens):
    
    
    cost_per_1k_tokens_input = 0.00015  # Adjust based on OpenAI's pricing for input tokens
    cost_per_1k_tokens_output = 0.00060  # Adjust based on OpenAI's pricing for output tokens
    
    input_cost = (all_prompt_tokens / 1000) * cost_per_1k_tokens_input
    output_cost = (all_completion_tokens / 1000) * cost_per_1k_tokens_output
    total_response_tokens = all_prompt_tokens + all_completion_tokens
    total_cost = input_cost + output_cost 
    
    logging.debug(f"Total Prompt Tokens: {all_prompt_tokens}, Total Completion Tokens: {all_completion_tokens}, "
                  f"Total Tokens: {total_response_tokens}, Input Cost: ${input_cost:.5f}, Output Cost: ${output_cost:.5f}, Total Cost: ${total_cost:.5f}")
    print(f"Total Prompt Tokens: {all_prompt_tokens}\nCompletion Tokens: {all_completion_tokens}\nTotal Tokens: {total_response_tokens}\nInput Cost: ${input_cost:.5f}\nOutput Cost: ${output_cost:.5f}\nTotal Cost: ${total_cost:.5f}")
    
    return total_cost, input_cost, output_cost
