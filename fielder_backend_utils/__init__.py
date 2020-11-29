from typing import List, Iterator

def hello_fielder():
    print("Hello Fielder")

def make_chunks(item_list: List, chunk_size: int) -> Iterator:
    """
    This function returns a generator 
    that yields chunks with size chunk_size, 
    with the possibility of the last chunk being smaller 
    if the len(item_list) does not divide by chunk_size.
    
    Args:
        item_list (List): list of objects to chunk
        chunk_size (int): chunk size
    Returns:
        chunk of items_list with size <= chunk_size
    """
    start = 0
    end = min(chunk_size, len(item_list))
    while start < len(item_list):
        yield item_list[start:end]
        start = end
        end = start + chunk_size
        end = min(end, len(item_list))

if __name__ == '__main__':
    pass
