from collections.abc import AsyncIterator

from app.core import config  # noqa: F401  (memastikan .env dimuat sebelum litellm)

import litellm

litellm.drop_params = True  # abaikan parameter yang tidak didukung provider
litellm.num_retries = 3     # coba ulang otomatis saat provider sibuk


async def stream_answer(model: str, messages: list[dict], max_tokens: int) -> AsyncIterator[str]:
    """Yield potongan teks dari LLM satu per satu."""
    resp = await litellm.acompletion(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        stream=True,
    )
    async for chunk in resp:
        text = chunk.choices[0].delta.content or ""
        if text:
            yield text