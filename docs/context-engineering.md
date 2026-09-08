# Context Engineering

## Write
Case facts and important synthetic facts are written into working/long-term memory.

## Select
`context/selector.py` selects only fields relevant to the current worker.

## Compress
`context/compressor.py` summarizes older messages when a thread exceeds the configured working window.

## Isolate
`context/quarantine.py` marks customer/order free-text as untrusted data. It is never injected as an instruction.
