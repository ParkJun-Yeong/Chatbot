import torch
from dataset import DementiaDataset, collate_fn
from torch.utils.data import DataLoader
import pandas as pd
from AlzhBERT import AlzhBERT
from utils import get_y_dec_list, get_y_enc_list

device = "cuda" if torch.cuda.is_available() else "cpu"


if __name__ == "__main__":
    test_dataset = DementiaDataset(is_ts=True)
    test_dataloader = DataLoader(test_dataset, batch_size=len(test_dataset), shuffle=False, collate_fn=collate_fn)
    mode = 'multi'

    if mode == "single":
        model = AlzhBERT(embedding_dim=768, mode="single").to(device)
        checkpoint = torch.load("./saved_model/221014_single_self_attention/2022-10-14-16-02-e69.pt")
    elif mode == "multi":
        model = AlzhBERT(embedding_dim=768, mode="multi").to(device)
        checkpoint = torch.load("./saved_model/221014_multi_self_attention/2022-10-14-21-43-e70.pt")

    model.load_state_dict(checkpoint["model_state_dict"])

    loss_fn = torch.nn.MSELoss()

    accuracy = []
    enc_loss = None
    dec_loss = None

    with torch.no_grad():
        model.eval()

        for X, y in test_dataloader:
            enc_preds, dec_preds = model(X)

            y = torch.tensor(y, dtype=torch.float32).to(device)
            y_enc = get_y_enc_list(X, y)
            y_dec = get_y_dec_list(X)

            y_enc = torch.tensor(y_enc,device=device)

            enc_preds = torch.stack(enc_preds).to(device)

            enc_loss = loss_fn(y_enc, enc_preds)

            dec_losses = []
            for i in range(len(dec_preds)):
                dec_losses.append(loss_fn(y_dec[i].to(device), dec_preds[i].to(device)))

            dec_losses = torch.stack(dec_losses)
            dec_loss = torch.mean(dec_losses)

            cls_out = [1 if enc >= 0.5 else 0 for enc in enc_preds]

            accuracy = torch.tensor([1 if cls == enc else 0 for cls, enc in zip(cls_out, y_enc)], dtype=torch.float32)
            # accuracy = torch.tensor(accuracy, dtype=torch.float32)
            accuracy = torch.mean(accuracy)

            print()




    result = pd.DataFrame({"avg_enc_loss-test": enc_loss,
                           "avg_dec_loss_test: ": dec_loss,
                           "avg_accuracy": accuracy})
    result.to_csv("./result/221014_single_attention/avg_dec_loss.csv")






