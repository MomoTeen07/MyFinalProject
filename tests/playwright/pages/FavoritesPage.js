export class FavoritesPage { constructor(page){this.page=page} async goto(){await this.page.goto('/favorites')} }
