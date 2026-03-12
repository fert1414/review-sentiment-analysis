def count_original_status(reviews: list) -> int | int:
    total_negative = 0
    total_positive = 0

    for item in reviews:
        if not item.rating:
            continue
        
        if item.rating <= 4:
            total_negative += 1
        elif item.rating >= 7:
            total_positive += 1
        else:
            continue

    return total_positive, total_negative