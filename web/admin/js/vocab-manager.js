import { Icons } from "./icons.js";

export class VocabManager {
  constructor(api, containerId, countId, onToast) {
    this.api = api;
    this.container = document.getElementById(containerId);
    this.countBadge = document.getElementById(countId);
    this.onToast = onToast;
    this.vocabList = [];

    this.modalBackdrop = document.getElementById("vocab-modal-backdrop");
    this.modalList = document.getElementById("modal-vocab-list");
    this.modalEmpty = document.getElementById("modal-vocab-empty");
    this.modalCount = document.getElementById("modal-vocab-count");
    this.searchInput = document.getElementById("modal-vocab-search");
    this.filterPills = document.querySelectorAll(".btn-modal-filter");
    this.openModalBtn = document.getElementById("open-vocab-modal-btn");
    this.closeModalBtn = document.getElementById("close-vocab-modal-btn");
    this.dismissModalBtn = document.getElementById("dismiss-vocab-modal-btn");

    this.activeCategory = "all";
    this.searchKeyword = "";

    this.initModalEvents();
  }

  initModalEvents() {
    if (this.openModalBtn) {
      this.openModalBtn.addEventListener("click", () => this.openModal());
    }

    if (this.closeModalBtn) {
      this.closeModalBtn.addEventListener("click", () => this.closeModal());
    }

    if (this.dismissModalBtn) {
      this.dismissModalBtn.addEventListener("click", () => this.closeModal());
    }

    if (this.modalBackdrop) {
      this.modalBackdrop.addEventListener("click", (e) => {
        if (e.target === this.modalBackdrop) {
          this.closeModal();
        }
      });
    }

    if (this.searchInput) {
      this.searchInput.addEventListener("input", (e) => {
        this.searchKeyword = (e.target.value || "").trim().toLowerCase();
        this.renderModal();
      });
    }

    if (this.filterPills && this.filterPills.length > 0) {
      this.filterPills.forEach((pill) => {
        pill.addEventListener("click", () => {
          this.filterPills.forEach((p) => p.classList.remove("active"));
          pill.classList.add("active");
          this.activeCategory = pill.getAttribute("data-cat") || "all";
          this.renderModal();
        });
      });
    }
  }

  openModal() {
    if (!this.modalBackdrop) return;
    this.modalBackdrop.style.display = "flex";
    this.modalBackdrop.setAttribute("aria-hidden", "false");
    if (this.searchInput) {
      this.searchInput.value = "";
      this.searchKeyword = "";
      setTimeout(() => this.searchInput.focus(), 80);
    }
    this.renderModal();
  }

  closeModal() {
    if (!this.modalBackdrop) return;
    this.modalBackdrop.style.display = "none";
    this.modalBackdrop.setAttribute("aria-hidden", "true");
  }

  isModalOpen() {
    return Boolean(this.modalBackdrop && this.modalBackdrop.style.display !== "none");
  }

  async load() {
    try {
      const data = await this.api.getVocabulary();
      this.vocabList = data.vocabulary || data.items || [];
      this.render();
      if (this.isModalOpen()) {
        this.renderModal();
      }
    } catch (err) {
      if (this.onToast) this.onToast("Gagal memuat kamus istilah");
    }
  }

  render() {
    if (!this.container) return;
    this.container.innerHTML = "";

    if (this.countBadge) {
      this.countBadge.textContent = `${this.vocabList.length} Istilah`;
    }

    this.vocabList.forEach((item) => {
      const chip = document.createElement("div");
      chip.className = `hotword-chip chip-cat-${item.category || "academic"}`;

      const text = document.createElement("span");
      text.className = "chip-text";
      text.textContent = item.term;

      const delBtn = document.createElement("button");
      delBtn.type = "button";
      delBtn.className = "chip-del-btn";
      delBtn.setAttribute("title", `Hapus "${item.term}"`);
      delBtn.innerHTML = Icons.trash;
      delBtn.addEventListener("click", () => this.remove(item.id || item.term, item.term));

      chip.appendChild(text);
      chip.appendChild(delBtn);
      this.container.appendChild(chip);
    });
  }

  renderModal() {
    if (!this.modalList) return;
    this.modalList.innerHTML = "";

    if (this.modalCount) {
      this.modalCount.textContent = `${this.vocabList.length} Istilah`;
    }

    const filtered = this.vocabList.filter((item) => {
      const matchCat = this.activeCategory === "all" || item.category === this.activeCategory;
      const matchSearch = !this.searchKeyword || item.term.toLowerCase().includes(this.searchKeyword);
      return matchCat && matchSearch;
    });

    if (filtered.length === 0) {
      if (this.modalEmpty) this.modalEmpty.style.display = "block";
      return;
    }

    if (this.modalEmpty) this.modalEmpty.style.display = "none";

    filtered.forEach((item) => {
      const card = document.createElement("div");
      card.className = "modal-item-card";

      const info = document.createElement("div");
      info.className = "modal-item-info";

      const termSpan = document.createElement("span");
      termSpan.className = "modal-item-term";
      termSpan.textContent = item.term;

      const catBadge = document.createElement("span");
      catBadge.className = `modal-item-category chip-cat-${item.category || "academic"}`;
      catBadge.textContent = item.category || "academic";

      info.appendChild(termSpan);
      info.appendChild(catBadge);

      const delBtn = document.createElement("button");
      delBtn.type = "button";
      delBtn.className = "chip-del-btn";
      delBtn.setAttribute("title", `Hapus "${item.term}"`);
      delBtn.innerHTML = Icons.trash;
      delBtn.addEventListener("click", () => this.remove(item.id || item.term, item.term));

      card.appendChild(info);
      card.appendChild(delBtn);
      this.modalList.appendChild(card);
    });
  }

  async add(term, category = "academic") {
    const cleanTerm = term.trim();
    if (!cleanTerm) return;

    try {
      await this.api.addVocabulary(cleanTerm, category);
      if (this.onToast) this.onToast(`Ditambahkan ke kamus: "${cleanTerm}"`);
      await this.load();
    } catch (err) {
      if (this.onToast) this.onToast(`Gagal menambahkan "${cleanTerm}"`);
    }
  }

  async remove(id, term) {
    try {
      await this.api.deleteVocabulary(id);
      if (this.onToast) this.onToast(`Dihapus: "${term}"`);
      await this.load();
    } catch (err) {
      if (this.onToast) this.onToast(`Gagal menghapus "${term}"`);
    }
  }
}
