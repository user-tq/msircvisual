import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu


def msiplot(
    baseline: pd.DataFrame | None, tumor: pd.DataFrame, output_file, mwu_test=True
):
    # 如果没有基线数据，则只绘制 tumor 数据
    has_baseline = baseline is not None

    # 获取所有列名（假设 baseline 和 tumor 的列名一致）
    columns = tumor.columns

    # 根据列名数量动态创建子图
    fig, axes = plt.subplots(len(columns), 1, figsize=(10, 8), sharex=True)
    if len(columns) == 1:
        axes = [axes]  # 如果只有一个子图，axes 是一个轴对象，而不是列表

    # 遍历每个列名并绘制数据
    for i, col in enumerate(columns):
        ax = axes[i]

        if has_baseline:
            # 绘制基线数据
            ax.plot(
                baseline.index,
                baseline[col],
                color="blue",
                linestyle="-",
                label="Baseline",
            )

        # 绘制肿瘤数据
        ax.plot(tumor.index, tumor[col], color="red", linestyle="-", label="Tumor")

        # 如果有基线数据，进行 Mann-Whitney U 检验
        if has_baseline and mwu_test:
            stat, p = mannwhitneyu(baseline[col], tumor[col], alternative="two-sided")
            p_value_text = f"p={p:.4f}"  # 格式化 p 值，显示为普通浮点数，保留 4 位小数
        else:
            p_value_text = ""

        # 将列名和 p 值一起显示在子图中
        ax.text(
            0.75,
            0.45,
            f"{col}\n{p_value_text}",
            transform=ax.transAxes,
            ha="right",
            va="center",
            fontsize=12,
        )

        # 动态调整纵轴刻度
        max_y = (
            max(tumor[col].max(), 20)
            if not has_baseline
            else max(max(baseline[col].max(), tumor[col].max()), 20)
        )
        y_ticks = list(range(0, int(max_y) + 1, 20))
        ax.set_yticks(y_ticks)

    # 设置共享的 x 轴和 y 轴标签
    fig.text(0.5, 0.04, "Microsates Repeat Times", ha="center", fontsize=14)
    fig.text(
        0.04,
        0.5,
        "Support Reads Number (normalization)",
        va="center",
        rotation="vertical",
        fontsize=14,
    )

    # 设置横轴刻度只展示10的倍数
    max_x = (
        tumor.index.max()
        if not has_baseline
        else max(baseline.index.max(), tumor.index.max())
    )
    x_ticks = list(range(0, int(max_x) + 1, 10))
    axes[-1].set_xticks(x_ticks)

    # 只保留一个图例
    handles, labels = axes[0].get_legend_handles_labels()
    if has_baseline:
        fig.legend(handles, labels, loc="upper right", bbox_to_anchor=(0.9, 0.9))
    else:
        fig.legend(
            [handles[0]], [labels[0]], loc="upper right", bbox_to_anchor=(0.9, 0.9)
        )

    # 调整布局
    plt.tight_layout(rect=[0.05, 0.05, 0.95, 0.95])

    # 保存图像
    plt.savefig(output_file)


if __name__ == "__main__":
    baseline = pd.read_csv("test/combined.tsv", sep="\t", index_col=0)
    tumor = pd.read_csv("test/tumor.tsv", sep="\t", index_col=0)

    # 使用示例
    msiplot(baseline, tumor, "test/combined.png")
